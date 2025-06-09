# util/ui_components

import logging
import os

import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from util.accessibility_report_viewer import AccessibilityReportViewer
from util.accessibility_tester import AccessibilityTester
from util.helper_functions import HelperFunctions


class UIComponents:
    """
    A class to manage the UI components of the Web Accessibility Checker.

    This class contains methods to render various parts of the UI, including
    headers, custom CSS, URL input forms, test choices, and results display.
    """

    def __init__(self):
        self.helper = HelperFunctions()

    @staticmethod
    def setup_header() -> None:
        """
        Sets up the header for the Streamlit application.
        """
        header_container = st.container()
        
        with header_container:
            base_path = os.path.dirname(__file__)
            image_path = os.path.join(base_path, "..", "static", "logo.webp")
            #image_path = os.path.join(base_path, "..", "static", "digitalagenten_Logo_quer-2.png")  # Adjust the path
            logo = Image.open(image_path)
            st.image(logo, width=300)
            #st.header("a11y Tool", divider='grey')
            st.markdown(
            """
            <h1 id="a11y-tool">a11y <span>Tool</span></h1><hr style="color: #586e75; background-color: #586e75; height:3px;  margin:-10px 15px">
            """,
            unsafe_allow_html=True
            )
            

    @staticmethod
    def setup_custom_css() -> None:
        """
        Sets up custom CSS for the Streamlit application.
        """
        st.markdown("""
            <style>
               
            #a11y-tool {
                text-align: right; 
                margin-top:-75px;
                color: #ff6400;     
            }
            
             #a11y-tool span {
                color: white;
            }
            
            @media only screen and (max-width: 600px)   {
                #a11y-tool {
                text-align: center;
                margin:auto;      
                }
                
            }  
                    
            #a11y-test-results {
                padding-left:10px;      
            }
                    
            .block-container {
                max-width: 100rem;
            }
            .block-container [data-testid="column"] {
                border: 3px solid #586e75;
                border-radius: 15px;
                padding: 10px;
                box-shadow: 1px 1px 1px rgba(49, 51, 63, 0.1);
            }
            @media only screen and (min-width: 600px)   {
            [role=radiogroup]{
                gap: 2rem;
                
            }
            }

            .stTextInput > label p {
                font-size: 105% !important; 
                font-weight: bold !important; 
                color: #FF6400;
            } 
            .stNumberInput > label p {font-size:105%; font-weight:bold; color:#FF6400;}
            .stMultiSelect > label p {font-size:105%; font-weight:bold; color:#FF6400;} 
            .stSelectbox > label p {font-size:105%; font-weight:bold; color:#FF6400;}
            .stRadio > label p {font-size:105%; font-weight:bold; color:#FF6400;} 

            .stPlotlyChart {
                display:flex;
                justify-content:center;
                margin-bottom:30px;
                }  

            [data-testid="stImage"] {
                padding-left:15px;
                margin-top:-30px;
                margin-bottom:-20px
                }  
            
            .stDeployButton {visibility: hidden;}
                    
            [data-testid="stHeader"] {
                background-color:transparent;
                }
                    
            
            
            </style>
            """, unsafe_allow_html=True)

    def build_find_urls_form(self, helper, WebsiteCrawler, SitemapParser) -> None:
        """
        Renders the container for finding URLs.

        Args:
            helper (HelperFunctions): The helper functions instance.
            WebsiteCrawler (WebsiteCrawler): The website crawler class.
            SitemapParser (SitemapParser): The sitemap parser class.
        """
        with st.form(key='find_urls_form'):
            st.subheader("Find URLs", divider="grey")
            url = st.text_input(label='Enter the URL of the website to check')
            crawl_depth = st.number_input('Set Crawl Depth', min_value=1, value=3)

            ### TODO
            # Check if a sitemap exists and set the session state
            #if url:
                #HelperFunctions.check_sitemap_and_set_state(url)

            # Inform the user if a sitemap was found
            #if st.session_state.sitemap_exists:
                #st.info("Sitemap found. You can choose to use the sitemap or crawl the website.")
            #else:
                #st.info("No sitemap found. Please choose Crawl to start crawling the website.")
            ###

            # Add a radio button to select the extraction method
            st.session_state.extraction_method = st.radio(
                "Choose how to extract URLs:",
                ('Test only entered URL', 'Use Sitemap', 'Crawl Website'),
                horizontal=True,
                index=None
            )

            find_urls_button = st.form_submit_button(label='Find URLs')

        if find_urls_button:
            st.session_state.show_tests = False
            helper.handle_url_extraction(url, crawl_depth, WebsiteCrawler, SitemapParser) 
             

    def handle_test_choice(self) -> None:
        """
        Handles the test choice selection and execution.

        This method renders the UI for choosing the type of accessibility test to run
        and initiates the test based on user selection.
        """
        if st.session_state.extracted_urls:
            with st.form(key='test_choice_form', clear_on_submit=True):
                st.subheader("Choose Test Type", divider="grey")
                test_choice = st.radio(
                    f"Select the URLs to test from {len(st.session_state.extracted_urls)} URLs:",
                    ('Test only homepage', 'Test all URLs', 'Select specific URLs'),
                    horizontal=True,
                    index=None
                )

                choice_made_button = st.form_submit_button(label='Confirm Choice')

            if choice_made_button:
                st.session_state.choice_made = True
                st.session_state.test_choice = test_choice
                st.session_state.axe_version = "latest"

            if st.session_state.choice_made:
                if 'tester' not in st.session_state:
                    st.session_state.tester = AccessibilityTester()

                if st.session_state.test_choice == 'Test all URLs':
                    self.perform_tests(st.session_state.tester, st.session_state.extracted_urls)
                elif st.session_state.test_choice == 'Test only homepage':
                    self.perform_tests(st.session_state.tester, {st.session_state.previous_url})
                elif st.session_state.test_choice == 'Select specific URLs':
                    self.perform_selected_tests(st.session_state.tester)
                
    def build_results_display(self, latest_results_directory: str) -> None:
        """
        Renders the container for displaying test results.

        Args:
            latest_results_directory (str): The directory containing the latest test results.
        """
        logging.info(f"Getting accessibility test results from CSV and JSON files in: {latest_results_directory}")

        json_result_files = [f for f in os.listdir(latest_results_directory) if f.endswith('.json')]
        display_names_to_file_paths = {
            self.helper.extract_domain_and_page_from_json(os.path.join(latest_results_directory, file_name)): file_name
            for file_name in json_result_files
        }

        sorted_display_names = sorted(display_names_to_file_paths.keys())
        selected_display_name = st.selectbox('Select a test result to view', options=sorted_display_names)

        selected_file_path = os.path.join(latest_results_directory, display_names_to_file_paths[selected_display_name]) if selected_display_name else None

        if selected_file_path:
            report_viewer = AccessibilityReportViewer(selected_file_path)
            logging.info(f"Displaying score for {selected_display_name}")
            score = report_viewer.calculate_accessibility_score()
            logging.info(f"Displaying violations for {selected_display_name}")
            violations_df = report_viewer.create_violations_dataframe()
            st.dataframe(violations_df)
            st.session_state['score'] = score  # Store the score in the session
            st.session_state['selected_file_path'] = selected_file_path # Store the selected display name in the session

    def build_gauge_and_download_display(self, latest_results_directory: str) -> None:
        """
        Renders the gauge chart and download options for test results.

        Args:
            latest_results_directory (str): The directory containing the latest test results.
        """
        score = st.session_state.get('score', 0)  # Retrieve the score from the session
        selected_file_path = st.session_state.get('selected_file_path', '')  # Retrieve the selected file path from the session

        self.display_gauge_chart(score)

        self.display_download_options(latest_results_directory, selected_file_path)

    def perform_tests(self, tester: AccessibilityTester, urls: set[str]) -> None:
        """
        Perform accessibility tests on the given URLs.

        Args:
            tester (AccessibilityTester): The tester instance to run the tests.
            urls (Set[str]): The set of URLs to test.
        """
        logging.info(f"Starting accessibility Tests from: {st.session_state.previous_url}")
        with st.spinner("Performing accessibility tests"):
            if urls:
                tester = AccessibilityTester()#
                results,axe_version = tester.test_urls(urls)
                if results:
                    st.success(f"Accessibility tests completed using Axe-Core version: {axe_version}")
                    logging.info(f"Finished accessibility Tests from: {st.session_state.previous_url} \n {len(urls)} URLs tested: {urls} using Axe-Core version: {axe_version} ")
                else:
                    st.error("An error occurred while checking the selected URLs.")
                    logging.error("Error: No results returned for the URLs")
            else:
                st.error("No URLs selected for testing.")
        st.session_state.show_tests = True

    def perform_selected_tests(self, tester: AccessibilityTester) -> None:
        """
        Perform accessibility tests on selected URLs.

        Args:
            tester (AccessibilityTester): The tester instance to run the tests.
        """
        with st.form(key='run_tests_form', clear_on_submit=True):
            #st.subheader("Select URLs to test", divider="grey")
            selected_urls: list[str] = st.multiselect("Select URLs to test", options=list(st.session_state.extracted_urls), default=None, placeholder="Choose URLs To Test")
            run_tests_button_pressed = st.form_submit_button(label='Run Accessibility Tests')
        if run_tests_button_pressed:
            self.perform_tests(tester, set(selected_urls))

    @staticmethod
    def display_gauge_chart(score: int) -> None:
        """
        Displays a gauge chart for the accessibility score.

        Args:
            score (int): The accessibility score to display.
        """
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': "Accessibility Score", 'font': {'size': 20}},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue", 'thickness': 0.2},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "grey",
                'steps': [
                    {'range': [0, 50], 'color': 'red'},
                    {'range': [50, 75], 'color': 'yellow'},
                    {'range': [75, 100], 'color': 'green'},
                ],
                'threshold': {
                    'line': {'color': "darkblue", 'width': 4},
                    'thickness': 0.75,
                    'value': score}
            }
        ))

        fig.update_layout(
            paper_bgcolor="#002b36",
            font={'color': "white", 'family': "Arial"},
            width=350,
            height=300, 
        )

        st.plotly_chart(fig)

    def display_download_options(self, latest_results_directory: str, selected_file_path: str) -> None:
        """
        Displays download options for test results based on the selected file path.

        Args:
            latest_results_directory (str): The directory containing the latest test results.
            selected_file_path (str): The path of the selected result file.
        """
        #st.write("Download Test Results")
    
        # Extract the filename without extension
        selected_file_name = os.path.splitext(os.path.basename(selected_file_path))[0]
        logging.info(f"Selected file name (without extension): {selected_file_name}")

        # Construct the expected filenames for JSON and CSV based on the selected file name
        json_file = f"{selected_file_name}.json"
        csv_file = f"{selected_file_name}.csv"
    
    # Check if the files exist in the directory
        json_file_path = os.path.join(latest_results_directory, json_file)
        csv_file_path = os.path.join(latest_results_directory, csv_file)
        logging.info(f"Checking if JSON file exists: {json_file_path} - {os.path.exists(json_file_path)}")
        logging.info(f"Checking if CSV file exists: {csv_file_path} - {os.path.exists(csv_file_path)}")
    
        files_to_download = []
        if os.path.exists(json_file_path):
            files_to_download.append(json_file)
        if os.path.exists(csv_file_path):
            files_to_download.append(csv_file)
        logging.info(f"Files available for download: {files_to_download}")
    
        download_file = st.selectbox('Select a test result to download', options=files_to_download, index=0)

        if download_file:
            file_path = os.path.join(latest_results_directory, download_file)
            with open(file_path, "rb") as fp:
                download_button_pressed = st.download_button(
                    label="Download File",
                    data=fp,
                    file_name=download_file,
                    mime="application/octet-stream"
                )

                if download_button_pressed:
                    st.session_state.download_initiated = True
                    logging.info(f'downloading {download_file}')
                if st.session_state.download_initiated:
                    st.session_state.download_initiated = False
                    