import sqlite3
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).with_name('helpdesk.db')
STATUSES = ['Open', 'In Progress', 'Resolved', 'Closed']
PRIORITIES = ['Low', 'Medium', 'High', 'Critical']
CATEGORIES = ['Hardware', 'Software', 'Network', 'Email & Accounts', 'Access & Permissions', 'Other']

st.set_page_config(page_title='ServiceDesk | IT Help Desk', page_icon='🛠️', layout='wide')
st.markdown('''<style>
.block-container{padding-top:1.7rem;padding-bottom:2rem} .hero{padding:1.25rem 1.5rem;border-radius:14px;background:linear-gradient(115deg,#10243b,#1d5274);color:white;margin-bottom:1.2rem}
.hero h1{color:white;margin:0;font-size:2rem}.hero p{color:#d7e8f4;margin:.35rem 0 0}.metric-card{border:1px solid rgba(128,128,128,.25);border-radius:12px;padding:12px 16px}
</style>''', unsafe_allow_html=True)


def connect():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requester TEXT NOT NULL,
            email TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            assigned_to TEXT DEFAULT '',
            resolution TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS ticket_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            note TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
        )''')


def get_tickets():
    with connect() as conn:
        return pd.read_sql_query('SELECT * FROM tickets ORDER BY created_at DESC', conn)


def add_ticket(data):
    now = datetime.now().isoformat(timespec='seconds')
    with connect() as conn:
        cur = conn.execute('''INSERT INTO tickets
            (requester,email,title,description,category,priority,status,assigned_to,created_at,updated_at)
            VALUES (?,?,?,?,?,?, 'Open',?,?,?)''',
            (data['requester'], data['email'], data['title'], data['description'], data['category'],
             data['priority'], data['assigned_to'], now, now))
        return cur.lastrowid


def update_ticket(ticket_id, status, priority, assigned_to, resolution):
    with connect() as conn:
        conn.execute('''UPDATE tickets SET status=?, priority=?, assigned_to=?, resolution=?, updated_at=? WHERE id=?''',
                     (status, priority, assigned_to, resolution, datetime.now().isoformat(timespec='seconds'), ticket_id))


def add_note(ticket_id, note, author):
    with connect() as conn:
        conn.execute('INSERT INTO ticket_notes(ticket_id,note,author,created_at) VALUES(?,?,?,?)',
                     (ticket_id, note, author, datetime.now().isoformat(timespec='seconds')))


def get_notes(ticket_id):
    with connect() as conn:
        return pd.read_sql_query('SELECT note,author,created_at FROM ticket_notes WHERE ticket_id=? ORDER BY created_at DESC', conn, params=(ticket_id,))


init_db()
st.markdown('<div class="hero"><h1>🛠️ ServiceDesk</h1><p>IT Help Desk & Incident Management Portal · Track, prioritise and resolve support requests</p></div>', unsafe_allow_html=True)

tickets = get_tickets()
if tickets.empty:
    open_count = progress_count = resolved_count = critical_count = 0
else:
    open_count = int((tickets.status == 'Open').sum())
    progress_count = int((tickets.status == 'In Progress').sum())
    resolved_count = int(tickets.status.isin(['Resolved', 'Closed']).sum())
    critical_count = int((tickets.priority == 'Critical').sum())

m1,m2,m3,m4 = st.columns(4)
m1.metric('Total tickets', len(tickets))
m2.metric('Open', open_count)
m3.metric('In progress', progress_count)
m4.metric('Resolved / closed', resolved_count)

pages = ['Dashboard', 'Create ticket', 'Manage tickets', 'Reports & export']
page = st.sidebar.radio('Navigation', pages)
st.sidebar.caption('Local demo application · SQLite database')

if page == 'Dashboard':
    st.subheader('Incident overview')
    if tickets.empty:
        st.info('No tickets yet. Create a ticket to populate the dashboard.')
    else:
        left, right = st.columns(2)
        with left:
            st.markdown('**Tickets by status**')
            st.bar_chart(tickets.status.value_counts())
        with right:
            st.markdown('**Tickets by priority**')
            st.bar_chart(tickets.priority.value_counts().reindex(PRIORITIES).fillna(0))
        st.markdown('**Recently updated tickets**')
        st.dataframe(tickets[['id','title','requester','category','priority','status','assigned_to','updated_at']].head(8), use_container_width=True, hide_index=True)

elif page == 'Create ticket':
    st.subheader('Submit a support request')
    with st.form('new_ticket', clear_on_submit=True):
        c1,c2 = st.columns(2)
        requester = c1.text_input('Requester name *')
        email = c2.text_input('Email address *')
        title = st.text_input('Issue title *', placeholder='e.g. Unable to connect to office Wi-Fi')
        description = st.text_area('Describe the issue *', placeholder='Include the error message, affected device/application and steps already tried.')
        c3,c4,c5 = st.columns(3)
        category = c3.selectbox('Category', CATEGORIES)
        priority = c4.selectbox('Priority', PRIORITIES, index=1)
        assigned_to = c5.text_input('Assign to (optional)')
        submitted = st.form_submit_button('Create ticket', type='primary')
        if submitted:
            if not all([requester.strip(), email.strip(), title.strip(), description.strip()]):
                st.error('Please complete all required fields.')
            elif '@' not in email or '.' not in email.split('@')[-1]:
                st.error('Enter a valid email address.')
            else:
                ticket_id = add_ticket({'requester':requester.strip(),'email':email.strip(),'title':title.strip(),
                    'description':description.strip(),'category':category,'priority':priority,'assigned_to':assigned_to.strip()})
                st.success(f'Ticket HD-{ticket_id:04d} created successfully.')

elif page == 'Manage tickets':
    st.subheader('Ticket queue')
    if tickets.empty:
        st.info('No tickets available.')
    else:
        f1,f2,f3 = st.columns(3)
        status_filter = f1.selectbox('Filter by status', ['All'] + STATUSES)
        priority_filter = f2.selectbox('Filter by priority', ['All'] + PRIORITIES)
        search = f3.text_input('Search tickets', placeholder='ID, title, requester...')
        filtered = tickets.copy()
        if status_filter != 'All': filtered = filtered[filtered.status == status_filter]
        if priority_filter != 'All': filtered = filtered[filtered.priority == priority_filter]
        if search.strip():
            q = search.lower().strip()
            filtered = filtered[filtered.apply(lambda r: q in ' '.join(map(str,[r.id,r.title,r.requester,r.email,r.category])).lower(), axis=1)]
        st.dataframe(filtered[['id','title','requester','category','priority','status','assigned_to','created_at']], use_container_width=True, hide_index=True)
        ids = filtered.id.astype(int).tolist()
        if ids:
            selected = st.selectbox('Select ticket to update', ids, format_func=lambda x: f'HD-{x:04d} · {tickets.loc[tickets.id == x, "title"].iloc[0]}')
            row = tickets[tickets.id == selected].iloc[0]
            with st.expander(f'Ticket HD-{selected:04d} details', expanded=True):
                st.write(row.description)
                st.caption(f'Requester: {row.requester} ({row.email}) · Created: {row.created_at}')
                with st.form(f'update_{selected}'):
                    a,b = st.columns(2)
                    new_status = a.selectbox('Status', STATUSES, index=STATUSES.index(row.status))
                    new_priority = b.selectbox('Priority', PRIORITIES, index=PRIORITIES.index(row.priority))
                    new_assignee = st.text_input('Assigned technician', value=row.assigned_to or '')
                    new_resolution = st.text_area('Resolution / work performed', value=row.resolution or '')
                    save = st.form_submit_button('Save ticket updates', type='primary')
                    if save:
                        update_ticket(selected,new_status,new_priority,new_assignee.strip(),new_resolution.strip())
                        st.success('Ticket updated. Refresh the page to see the latest values.')
                st.markdown('**Internal troubleshooting notes**')
                with st.form(f'note_{selected}'):
                    author = st.text_input('Technician name', value='Support Technician')
                    note = st.text_area('Add a note')
                    note_submit = st.form_submit_button('Add note')
                    if note_submit:
                        if note.strip():
                            add_note(selected,note.strip(),author.strip() or 'Support Technician')
                            st.success('Note added.')
                        else: st.warning('Enter a note first.')
                notes = get_notes(selected)
                if not notes.empty:
                    for _, n in notes.iterrows(): st.write(f"**{n.author}** · {n.created_at}\n\n{n.note}")

elif page == 'Reports & export':
    st.subheader('Reports and data export')
    if tickets.empty:
        st.info('Create tickets before generating a report.')
    else:
        st.write('**Category breakdown**')
        st.dataframe(tickets.groupby('category').size().reset_index(name='ticket_count'), use_container_width=True, hide_index=True)
        st.write('**Priority and status summary**')
        summary = tickets.groupby(['priority','status']).size().reset_index(name='ticket_count')
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.download_button('Download all tickets (CSV)', tickets.to_csv(index=False).encode('utf-8'), 'helpdesk_tickets.csv', 'text/csv', type='primary')
        st.caption('Export contains ticket records. Keep personal information secure when sharing reports.')

st.divider()
st.caption('ServiceDesk demo · Built with Python, Streamlit and SQLite')
