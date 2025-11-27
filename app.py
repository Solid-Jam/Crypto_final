import streamlit as st
from database import get_db_connection
import sqlite3
from database import create_database

create_database()


def get_users_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users")
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_user_to_db(username: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    finally:
        conn.close()


def delete_user_from_db(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_assets_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, symbol, type, price FROM assets")
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_asset_to_db(name: str, symbol: str, type_: str, price: float):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO assets (name, symbol, type, price) VALUES (?, ?, ?, ?)",
        (name, symbol, type_, str(price))
    )
    conn.commit()
    conn.close()


def delete_asset_from_db(asset_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0



def login(username: str, password: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False
    stored_password = row["password"]
    return stored_password == password


# ----------------------
# Streamlit UI
# ----------------------

st.set_page_config(page_title="CryptoTracker Admin", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None


with st.sidebar:
    st.title("CryptoTracker")
    if st.session_state.logged_in:
        st.markdown(f"**Logged in as:** {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
    else:
        st.info("Please login or register to manage users and assets.")

    st.markdown("---")
    page = st.radio("Navigate", ["Login", "Register", "Users", "Assets"])


# Page: Login
if page == "Login":
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Logged in successfully")
            st.rerun()
        else:
            st.error("Invalid username or password")


# Page: Register
elif page == "Register":
    st.header("Register a new account")
    new_username = st.text_input("Choose a username", key="reg_user")
    new_password = st.text_input("Choose a password", type="password", key="reg_pass")
    if st.button("Register"):
        if not new_username or not new_password:
            st.error("Please provide both username and password")
        else:
            ok, err = add_user_to_db(new_username, new_password)
            if ok:
                st.success("Account created. You can now login.")
            else:
                st.error(f"Failed to create account: {err}")


# Page: Users management
elif page == "Users":
    st.header("Users Management")
    if not st.session_state.logged_in:
        st.warning("You must be logged in to view and manage users.")
    else:
        users = get_users_from_db()
        if users:
            st.subheader("Existing users")
            cols = st.columns([1, 3, 3, 2])
            cols[0].write("ID")
            cols[1].write("Username")
            cols[2].write("Password")
            cols[3].write("Action")

            for row in users:
                rcols = st.columns([1, 3, 3, 2])
                rcols[0].write(row["id"])
                rcols[1].write(row["username"])
                rcols[2].write(row["password"])  # <-- display password
                if rcols[3].button("Delete", key=f"del_user_{row['id']}"):
                    deleted = delete_user_from_db(row["id"])
                    if deleted:
                        st.success("User deleted")
                        st.rerun()
                    else:
                        st.error("Failed to delete user")
        else:
            st.info("No users found")

        st.markdown("---")
        st.subheader("Add user")
        u_name = st.text_input("Username to add", key="add_user_name")
        u_pass = st.text_input("Password", type="password", key="add_user_pass")
        if st.button("Add user"):
            if not u_name or not u_pass:
                st.error("Provide both username and password")
            else:
                ok, err = add_user_to_db(u_name, u_pass)
                if ok:
                    st.success("User added")
                    st.rerun()
                else:
                    st.error(f"Failed to add user: {err}")


# Page: Assets management
elif page == "Assets":
    st.header("Assets Management")
    if not st.session_state.logged_in:
        st.warning("You must be logged in to view and manage assets.")
    else:
        assets = get_assets_from_db()
        if assets:
            st.subheader("Existing assets")
            cols = st.columns([1, 2, 2, 2, 2])
            cols[0].write("ID")
            cols[1].write("Name")
            cols[2].write("Symbol")
            cols[3].write("Type")
            cols[4].write("Price")

            for row in assets:
                rcols = st.columns([1, 2, 2, 2, 2])
                rcols[0].write(row["id"])
                rcols[1].write(row["name"])
                rcols[2].write(row["symbol"])
                rcols[3].write(row["type"])
                rcols[4].write(row["price"])
                if rcols[4].button("Delete", key=f"del_asset_{row['id']}"):
                    deleted = delete_asset_from_db(row["id"])
                    if deleted:
                        st.success("Asset deleted")
                        st.rerun()
                    else:
                        st.error("Failed to delete asset")
        else:
            st.info("No assets found")

        st.markdown("---")
        st.subheader("Add asset")
        a_name = st.text_input("Name", key="asset_name")
        a_symbol = st.text_input("Symbol", key="asset_symbol")
        a_type = st.text_input("Type", key="asset_type")
        a_price = st.text_input("Price", key="asset_price")
        if st.button("Add asset"):
            try:
                price_f = float(a_price)
            except Exception:
                st.error("Price must be a number")
                price_f = None

            if not a_name or not a_symbol or not a_type or price_f is None:
                st.error("Please provide all asset fields")
            else:
                add_asset_to_db(a_name, a_symbol, a_type, price_f)
                st.success("Asset added")
                st.rerun()

