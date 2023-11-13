
import streamlit as st
import summarize_lib as glib

st.set_page_config(layout="wide", page_title="문서 요약")
st.title("문서 요약")

uploaded_file = st.file_uploader("Select a PDF", type=['pdf'])

upload_button = st.button("Upload", type="primary")

if upload_button:
    with st.spinner("Uploading..."):
        
        upload_response = glib.save_file(file_bytes=uploaded_file.getvalue())

        st.success(upload_response)
        
        st.session_state.has_document = True

if 'has_document' in st.session_state: #문서가 업로드되었는지 확인하기
    
    return_intermediate_steps = st.checkbox("중간 단계 요약 보기", value=True)
    summarize_button = st.button("요약하기", type="primary")
    
    if summarize_button:
        st.subheader("통합 요약")

        with st.spinner("Running..."):
            response_content = glib.get_summary(return_intermediate_steps=return_intermediate_steps)


        if return_intermediate_steps:

            st.write(response_content["output_text"])

            st.subheader("중간 단계 요약")

            for step in response_content["intermediate_steps"]:
                st.write(step)
                st.markdown("---")

        else:
            st.write(response_content)
