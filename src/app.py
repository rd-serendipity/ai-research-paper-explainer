import asyncio
import time
import streamlit as st

from LLMSelect import LLMSelector
from asyncExplainer import AsyncExplanationGenerator
from preprocessor import PaperPreprocessor

class StreamlitApp:
    def __init__(self):
        st.set_page_config(page_title="Research Paper Explainer", layout="wide")
        self.set_custom_css()

    def set_custom_css(self):
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
        
        :root {
            --background-color: #f0f4f8;
            --text-color: #1a1a1a;
            --card-background: #ffffff;
            --button-color: #4CAF50;
            --button-hover-color: #45a049;
            --border-color: #e0e0e0;
            --header-color: #2c3e50;
            --subheader-color: #34495e;
            --alert-background: #e3f2fd;
            --alert-text: #0d47a1;
            --paper-summary-background: #e8f5e9;
            --paper-summary-border: #4CAF50;
            --chunk-header-background: #3498db;
            --chunk-header-text: white;
            --section-separator: #d1d5db;
        }

        .dark-theme {
            --background-color: #1e1e1e;
            --text-color: #f0f0f0;
            --card-background: #2d2d2d;
            --button-color: #388e3c;
            --button-hover-color: #2e7d32;
            --border-color: #4a4a4a;
            --header-color: #bb86fc;
            --subheader-color: #03dac6;
            --alert-background: #1a237e;
            --alert-text: #8c9eff;
            --paper-summary-background: #1b5e20;
            --paper-summary-border: #4CAF50;
            --chunk-header-background: #1565c0;
            --chunk-header-text: #e3f2fd;
            --section-separator: #4a4a4a;
        }
        
        body {
            font-family: 'Roboto', sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .main > div {
            padding-top: 2rem;
        }
        
        .stButton > button {
            width: 100%;
            background-color: var(--button-color);
            color: var(--chunk-header-text);
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        
        .stButton > button:hover {
            background-color: var(--button-hover-color);
        }
        
        .stTextInput > div > div > input {
            background-color: var(--card-background);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            color: var(--text-color);
        }
        
        .stSelectbox > div > div > select {
            background-color: var(--card-background);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            color: var(--text-color);
        }
        
        h1 {
            color: var(--header-color);
            font-family: 'Roboto', sans-serif;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        
        h2 {
            color: var(--subheader-color);
            font-family: 'Roboto', sans-serif;
            font-weight: 400;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }
        
        .stAlert > div {
            padding: 0.75rem 1rem;
            border-radius: 4px;
            background-color: var(--alert-background);
            color: var(--alert-text);
        }
        
        .chunk-text, .explanation-text {
            background-color: var(--card-background);
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        }
        
        .sidebar .stRadio > div {
            background-color: var(--card-background);
            padding: 0.5rem;
            border-radius: 4px;
            margin-bottom: 0.5rem;
        }
        
        .stProgress > div > div > div > div {
            background-color: var(--button-color);
        }
        
        .paper-summary {
            background-color: var(--paper-summary-background);
            border-left: 5px solid var(--paper-summary-border);
            padding: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .chunk-header {
            background-color: var(--chunk-header-background);
            color: var(--chunk-header-text);
            padding: 0.5rem 1rem;
            border-radius: 4px 4px 0 0;
            margin-bottom: 0;
        }

        .section-separator {
            border-top: 1px solid var(--section-separator);
            margin: 1rem 0;
        }
        
        </style>
        """, unsafe_allow_html=True)

    def sidebar_content(self):
        with st.sidebar:
            st.title("Configuration")
            
            uploaded_file = st.file_uploader('Upload Research Paper (PDF)', type='pdf')
            
            model_lst = [
                'llama-3.1-70b-versatile',
                'llama3-70b-8192',
                'llama3-8b-8192',
                'llama-3.1-8b-instant',
                'mixtral-8x7b-32768-groq',
                'gemma-7b-it',
                'gemma2-9b-it',
                'gemini-pro',
                'gemini-1.5-pro',
                'gemini-1.5-flash',
                'gpt-4o',
                'gpt-4o-mini',
                'gpt-4-turbo',
                'gpt-4',
                'gpt-3.5-turbo',
                'chatgpt-4o-latest',
                'claude-3-opus-20240229',
                'claude-3-sonnet-20240229',
                'claude-3-haiku-20240307',
                'mistral-large-2402',
                'mistral-large-2407',
            ]
        
            model_name = st.selectbox('Choose Model', model_lst)
            name_to_api_provider = {
                'llama3-8b-8192': 'groq',
                'llama3-70b-8192': 'groq',
                'llama-3.1-70b-versatile': 'groq',
                'llama-3.1-8b-instant': 'groq',
                'mixtral-8x7b-32768-groq': 'groq',
                'gemma-7b-it': 'groq',
                'gemma2-9b-it': 'groq',
                'gemini-pro': 'google',
                'gemini-1.5-pro': 'google',
                'gemini-1.5-flash': 'google',
                'gpt-4o': 'openai',
                'gpt-4o-mini': 'openai',
                'gpt-4-turbo': 'openai',
                'gpt-4': 'openai',
                'gpt-3.5-turbo': 'openai',
                'chatgpt-4o-latest': 'openai',
                'claude-3-opus-20240229': 'anthropic',
                'claude-3-sonnet-20240229': 'anthropic',
                'claude-3-haiku-20240307': 'anthropic',
                'mistral-large-2402': 'mistralai',
                'mistral-large-2407': 'mistralai'
            }
            
            st.subheader("Explanation Options")
            options = {
                "difficulty": st.select_slider("Difficulty Level", ["High School", "Undergraduate", "Graduate", "Expert"]),
                "include_examples": st.checkbox("Include Examples", value=False),
                "explain_prereq": st.checkbox("Explain Prerequisites", value=False),
                "explain_math": st.checkbox("Explain Mathematical Concepts", value=False),
                "find_similar_papers": st.checkbox("Find Similar Papers", value=False, disabled=True)
            }
            
            if options["find_similar_papers"]:
                options["include_paper_summary"] = st.checkbox("Include Summary of Similar Papers", value=False, disabled=True)
            else:
                options["include_paper_summary"] = False
                st.info("'Find Similar Papers' feature is currently unavailable")
            
            with st.expander("Additional Options"):
                execution_mode = st.radio("Execution Mode", ["Async", "Non-Async"])
                
                if execution_mode == "Non-Async":
                    options["sleep_between"] = st.checkbox("Include Sleeps", value=False)
                else:
                    options["sleep_between"] = False
                
                summarization_method = st.selectbox("Summarization Method", ["map_reduce", "refine", "stuff"])
            
            return uploaded_file, model_name, name_to_api_provider[model_name], options, execution_mode, summarization_method

    def main_content(self, uploaded_file, model_name, api_provider, options, execution_mode, summarization_method):
        st.title('Research Paper Explainer')
        st.write("Upload a research paper PDF and get an explanation tailored to your needs.")

        if uploaded_file:
            if st.button('Process Paper'):
                if execution_mode == "Async":
                    asyncio.run(self.process_paper_async(uploaded_file, model_name, api_provider, options, summarization_method))
                else:
                    self.process_paper_sync(uploaded_file, model_name, api_provider, options, summarization_method)
        elif not uploaded_file:
            st.info('Please upload a PDF file in the sidebar to begin.')

    async def process_paper_async(self, uploaded_file, model_name, api_provider, options, summarization_method):
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Extracting text from PDF...")
        paper_text = PaperPreprocessor.extract_text_from_pdf(uploaded_file)

        status_text.text(f"Initializing {model_name} model from {api_provider}...")
        llm = LLMSelector.get_llm(api_provider, model_name)
        generator = AsyncExplanationGenerator(llm)

        progress_bar.progress(10)
        status_text.text("Summarizing the paper...")
        summary = generator.summarize_paper(paper_text, summarization_method)
        paper_chunks = generator.text_splitter.split_text(paper_text)

        progress_bar.progress(30)
        status_text.text("Generating explanations...")
        
        tasks = [
            generator.generate_main_explanation_async(summary, paper_chunks, difficulty=options['difficulty']),
            generator.generate_examples_async(summary, paper_chunks) if options['include_examples'] else None,
            generator.explain_prerequisites_async(summary, paper_chunks) if options["explain_prereq"] else None,
            generator.explain_math_async(summary, paper_chunks) if options["explain_math"] else None,
            generator.find_similar_papers_async(summary, options["include_paper_summary"]) if options["find_similar_papers"] else None
        ]
        results = await asyncio.gather(*[task for task in tasks if task is not None])

        explanations = {
            'Prerequisites': results[2] if options["explain_prereq"] else None,
            'Main Explanation': results[0],
            'Examples': results[1] if options['include_examples'] else None,
            'Mathematical Concepts': results[3] if options["explain_math"] else None,
            'Similar Papers': results[4] if options["find_similar_papers"] else None
        }
        explanations = {k: v for k, v in explanations.items() if v is not None}

        progress_bar.progress(90)
        status_text.text("Combining explanations...")
        final_explanation = generator.combine_explanations(summary, explanations, paper_chunks)

        progress_bar.progress(100)
        status_text.text("Displaying results...")
        self.display_results(summary, final_explanation)
        status_text.text('Process Completed!')

    def process_paper_sync(self, uploaded_file, model_name, api_provider, options, summarization_method):
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Extracting text from PDF...")
        paper_text = PaperPreprocessor.extract_text_from_pdf(uploaded_file)

        status_text.text(f"Initializing {model_name} model from {api_provider}...")
        llm = LLMSelector.get_llm(api_provider, model_name)
        generator = AsyncExplanationGenerator(llm)

        progress_bar.progress(10)
        status_text.text("Summarizing the paper...")
        summary = generator.summarize_paper(paper_text, summarization_method)

        if options["sleep_between"]:
            status_text.text("Sleeping for 60 seconds...")
            time.sleep(60)

        paper_chunks = generator.text_splitter.split_text(paper_text)

        progress_bar.progress(30)
        status_text.text("Generating explanations...")
        explanations = {}
        
        explanations['Main Explanation'] = generator.generate_main_explanation_sync(summary, paper_chunks, difficulty=options['difficulty'])

        if options["sleep_between"]:
            status_text.text("Sleeping for 60 seconds...")
            time.sleep(60)

        progress_bar.progress(50)
        
        if options['include_examples']:
            explanations['Examples'] = generator.generate_examples_sync(summary, paper_chunks)
            if options["sleep_between"]:
                status_text.text("Sleeping for 60 seconds...")
                time.sleep(60)

        progress_bar.progress(60)
        
        if options["explain_prereq"]:
            explanations['Prerequisites'] = generator.explain_prerequisites_sync(summary, paper_chunks)
            if options["sleep_between"]:
                status_text.text("Sleeping for 60 seconds...")
                time.sleep(60)
        progress_bar.progress(70)
        
        if options["explain_math"]:
            explanations['Mathematical Concepts'] = generator.explain_math_sync(summary, paper_chunks)
            if options["sleep_between"]:
                status_text.text("Sleeping for 60 seconds...")
                time.sleep(60)
        progress_bar.progress(80)
        
        if options["find_similar_papers"]:
            explanations['Similar Papers'] = generator.find_similar_papers_sync(summary, options["include_paper_summary"])
            if options["sleep_between"]:
                status_text.text("Sleeping for 60 seconds...")
                time.sleep(60)

        progress_bar.progress(90)
        status_text.text("Combining explanations...")
        final_explanation = generator.combine_explanations(summary, explanations, paper_chunks)

        progress_bar.progress(100)
        status_text.text("Displaying results...")
        self.display_results(summary, final_explanation)
        status_text.text('Process Completed!')

    def display_results(self, summary, final_explanation):
        st.success('Paper processed successfully!')
        
        st.markdown("## Paper Summary")
        st.markdown(f'<div class="paper-summary">{summary}</div>', unsafe_allow_html=True)
        
        chunks = final_explanation.split("## Chunk")
        for i, chunk in enumerate(chunks[1:], 1):
            st.markdown(f'<h2 class="chunk-header">Chunk {i}</h2>', unsafe_allow_html=True)
            
            sections = chunk.split("###")
            chunk_content = sections[0].strip()
            if chunk_content:
                st.markdown(f'<div class="chunk-text">{chunk_content}</div>', unsafe_allow_html=True)
            
            for section in sections[1:]:
                section_parts = section.split("\n", 1)
                if len(section_parts) == 2:
                    section_title, section_content = section_parts
                    st.markdown(f'<h3>{section_title.strip()}</h3>', unsafe_allow_html=True)
                    st.markdown(f'<div class="explanation-text">{section_content.strip()}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="section-separator"></div>', unsafe_allow_html=True)


    def run(self):
        uploaded_file, model_name, api_provider, options, execution_mode, summarization_method = self.sidebar_content()
        self.main_content(uploaded_file, model_name, api_provider, options, execution_mode, summarization_method)

if __name__ == '__main__':
    app = StreamlitApp()
    app.run()