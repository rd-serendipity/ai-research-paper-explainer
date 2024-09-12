import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains.summarize.chain import load_summarize_chain
from langchain.prompts import PromptTemplate

class AsyncExplanationGenerator:
    def __init__(self, llm):
        self.llm = llm
        self.search = 'search'  # PLACEHOLDER (FUTURE FEATURES)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=400)

    def summarize_paper(self, paper_text, summarization_method='map_reduce'):
        docs = [Document(page_content=text) for text in self.text_splitter.split_text(paper_text)]
        chain = load_summarize_chain(llm=self.llm, chain_type=summarization_method)
        return chain.invoke(docs)['output_text']


    async def process_chunk_async(self, summary, chunk, prompt_template, difficulty=None):
        input_dict = {'summary': summary, 'chunk': chunk}
        if difficulty is not None:
            input_dict['difficulty'] = difficulty

        chain = prompt_template | self.llm
        return (await chain.ainvoke(input_dict)).content

    def process_chunk_sync(self, summary, chunk, prompt_template, difficulty=None):
        input_dict = {'summary': summary, 'chunk': chunk}
        if difficulty is not None:
            input_dict['difficulty'] = difficulty

        chain = prompt_template | self.llm
        return chain.invoke(input_dict).content

    async def generate_main_explanation_async(self, summary, paper_chunks, difficulty):
        prompt = PromptTemplate(
            input_variables=['summary', 'chunk', 'difficulty'],
            template="Given the following summary of a research paper:\n\n{summary}\n\n"
                     "Explain the following part of the paper for a {difficulty} level reader:\n\n{chunk}\n\n"
                     "Provide a clear and concise explanation of the main ideas, methodology, and findings in this part, "
                     "considering how it fits into the overall paper."
        )
        tasks = [self.process_chunk_async(summary, chunk, prompt, difficulty) for chunk in paper_chunks]
        return await asyncio.gather(*tasks)

    def generate_main_explanation_sync(self, summary, paper_chunks, difficulty):
        prompt = PromptTemplate(
            input_variables=['summary', 'chunk', 'difficulty'],
            template="Given the following summary of a research paper:\n\n{summary}\n\n"
                     "Explain the following part of the paper for a {difficulty} level reader:\n\n{chunk}\n\n"
                     "Provide a clear and concise explanation of the main ideas, methodology, and findings in this part, "
                     "considering how it fits into the overall paper."
        )
        return [self.process_chunk_sync(summary, chunk, prompt, difficulty) for chunk in paper_chunks]

    async def generate_examples_async(self, summary, paper_chunks):
        prompt = PromptTemplate(
            input_variables=["summary", "chunk"],
            template="Given the following summary of a research paper:\n\n{summary}\n\n"
                     "Based on this part of the paper:\n\n{chunk}\n\n"
                     "Provide concrete examples that illustrate the main concepts or findings in this section."
        )
        tasks = [self.process_chunk_async(summary, chunk, prompt) for chunk in paper_chunks]
        return await asyncio.gather(*tasks)

    def generate_examples_sync(self, summary, paper_chunks):
        prompt = PromptTemplate(
            input_variables=["summary", "chunk"],
            template="Given the following summary of a research paper:\n\n{summary}\n\n"
                     "Based on this part of the paper:\n\n{chunk}\n\n"
                     "Provide concrete examples that illustrate the main concepts or findings in this section."
        )
        return [self.process_chunk_sync(summary, chunk, prompt) for chunk in paper_chunks]

    async def explain_prerequisites_async(self, summary, paper_chunks):
        prompt = PromptTemplate(
            input_variables=["summary", "chunk"],
            template="Given the following summary of a research paper:\n\n{summary}\n\n"
                     "For this part of the paper:\n\n{chunk}\n\n"
                     "Identify and explain the key prerequisites needed to understand this section."
        )
        tasks = [self.process_chunk_async(summary, chunk, prompt) for chunk in paper_chunks]
        return await asyncio.gather(*tasks)

    def explain_prerequisites_sync(self, summary, paper_chunks):
        prompt = PromptTemplate(
            input_variables=["summary", "chunk"],
            template="Given the following summary of a research paper:\n\n{summary}\n\n"
                     "For this part of the paper:\n\n{chunk}\n\n"
                     "Identify and explain the key prerequisites needed to understand this section."
        )
        return [self.process_chunk_sync(summary, chunk, prompt) for chunk in paper_chunks]

    async def explain_math_async(self, summary, paper_chunks):
        prompt = PromptTemplate(
            input_variables=["summary", "chunk"],
            template="Given the following summary of a research paper:\n\n{summary}\n\n"
                     "For this part of the paper:\n\n{chunk}\n\n"
                     "Explain in detail the key mathematical concepts and equations in this section."
                     "If no mathematical concept or equations are there return an empty string, don't make up anything up"
        )
        tasks = [self.process_chunk_async(summary, chunk, prompt) for chunk in paper_chunks]
        return await asyncio.gather(*tasks)

    def explain_math_sync(self, summary, paper_chunks):
        prompt = PromptTemplate(
            input_variables=["summary", "chunk"],
            template="Given the following summary of a research paper:\n\n{summary}\n\n"
                     "For this part of the paper:\n\n{chunk}\n\n"
                     "Explain in detail the key mathematical concepts and equations in this section."
                     "If no mathematical concept or equations are there return an empty string, don't make up anything up"
        )
        return [self.process_chunk_sync(summary, chunk, prompt) for chunk in paper_chunks]

    async def generate_search_query(self, summary):
        prompt = PromptTemplate(
            input_variables=["summary"],
            template="Based on the following summary of a research paper, suggest keywords for finding similar papers:\n\n{summary}\n\nKeywords:"
        )
        websearch_prompt = PromptTemplate(
            input_variables=['keywords'],
            template="Based on {keywords} make an web search optimized query for searching similar research papers on site:arxiv.org OR site:scholar.google.com"
        )
        chain = prompt | self.llm | websearch_prompt | self.llm
        keywords = await chain.ainvoke({'summary': summary})
        return keywords.content

    async def find_similar_papers_async(self, summary, include_summary=False):
        search_query = await self.generate_search_query(summary)
        search_results = await self.search.arun(search_query)

        if include_summary:
            prompt = PromptTemplate(
                input_variables=["summary", "search_results"],
                template="Given this summary of a research paper:\n\n{summary}\n\n"
                         "And based on the following search results, provide a brief summary of 2-3 similar research papers:\n\n{search_results}"
            )
            chain = prompt | self.llm
            return (await chain.ainvoke({'summary': summary, 'search_results': search_results})).content

        return search_results

    def find_similar_papers_sync(self, summary, include_summary=False):
        search_query = self.generate_search_query(summary)
        search_results = self.search.run(search_query)

        if include_summary:
            prompt = PromptTemplate(
                input_variables=["summary", "search_results"],
                template="Given this summary of a research paper:\n\n{summary}\n\n"
                         "And based on the following search results, provide a brief summary of 2-3 similar research papers:\n\n{search_results}"
            )
            chain = prompt | self.llm
            return chain.invoke({'summary': summary, 'search_results': search_results}).content

        return search_results

    def combine_explanations(self, summary, explanations, paper_chunks):
        combined_text = f"# Paper Summary\n\n{summary}\n\n"

        for i, chunk in enumerate(paper_chunks):
            combined_text += f"\n\n## Chunk {i+1}\n\n"
            combined_text += f"{chunk}\n\n"

            if "Prerequisites" in explanations:
                combined_text += f"### Prerequisites\n\n{explanations['Prerequisites'][i]}\n\n"

            combined_text += f"### Explanation\n\n{explanations['Main Explanation'][i]}\n\n"

            if "Examples" in explanations:
                combined_text += f"### Examples\n\n{explanations['Examples'][i]}\n\n"

            if "Mathematical Concepts" in explanations:
                math_content = explanations['Mathematical Concepts'][i]
                if math_content.strip():  # Only include if there's actual content
                    combined_text += f"### Mathematical Concepts\n\n{math_content}\n\n"

        if "Similar Papers" in explanations:
            combined_text += f"# Similar Papers\n\n{explanations['Similar Papers']}\n\n"

        return combined_text