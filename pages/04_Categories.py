import streamlit as st

from services.categories import list_categories, add_category, rename_category, delete_category

from ui.styles import inject_theme

inject_theme()

st.title("Categories")

st.subheader("Add a category")
with st.form("add_category_form", clear_on_submit=True):
    new_name = st.text_input("Category name")
    submitted = st.form_submit_button("Add", type="primary")
    if submitted:
        try:
            add_category(new_name)
            st.cache_data.clear()
            st.success(f"Added '{new_name}'.")
        except ValueError as e:
            st.error(str(e))

st.divider()
st.subheader("Existing categories")

categories = list_categories()

if not categories:
    st.info("No categories yet.")
else:
    for c in categories:
        with st.container(border=True):
            st.write(c["name"])

            new_name = st.text_input(
                "Rename to", value=c["name"],
                key=f"rename_{c['category_id']}", label_visibility="collapsed"
            )

            btn_col1, btn_col2, _ = st.columns([1, 1, 3])

            with btn_col1:
                if st.button("Save", key=f"save_{c['category_id']}", use_container_width=True):
                    try:
                        rename_category(c["category_id"], new_name)
                        st.cache_data.clear()
                        st.success("Renamed.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

            with btn_col2:
                if st.button("Delete", key=f"delete_{c['category_id']}", use_container_width=True):
                    try:
                        delete_category(c["category_id"])
                        st.cache_data.clear()
                        st.success("Deleted.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))