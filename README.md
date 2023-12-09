# Web Accessibility Checker

The Web Accessibility Checker is a Streamlit-based application that allows you to assess the accessibility of a website. It automates the process of crawling a website for URLs, running accessibility tests, and presenting the results in an easy-to-understand format.

## Features

- **URL Extraction:** Automatically crawls a given website to find all accessible URLs.
- **Accessibility Tests:** Runs a series of automated tests on each URL to check for accessibility issues.
- **Results Visualization:** Displays the accessibility score and details about any issues found.
- **Downloadable Reports:** Provides options to download detailed reports in JSON and CSV formats.

## Installation

To set up the Web Accessibility Checker on your local system, follow these steps:

1. Clone the repository from GitHub.
2. Ensure you have Python installed on your system.
3. Navigate to the project directory and install the required packages using `pip install -r requirements.txt`.
4. Run the Streamlit application with `streamlit run web_accessibility_checker.py`.

## Usage

### Starting the Application

After launching the application, you'll be greeted with a simple and intuitive interface.

### Finding URLs

1. Enter the base URL of the website you want to check in the input field.
2. Set the crawl depth to control how deep the crawl should go.
3. Click on the "Find URLs" button to start the crawling process.

### Choosing Test Type

Once the URLs are extracted:

1. Select the type of test you want to perform:
    - Test only homepage
    - Test all URLs
    - Select specific URLs
2. If you choose to select specific URLs, a multi-select box will appear where you can choose which URLs to test.
3. Confirm your choice to proceed with the tests.

### Running Accessibility Tests

Click on the "Run Accessibility Tests" button to start the accessibility tests on the chosen URLs.

### Viewing Results

After the tests are complete:

- The "Accessibility Test Results" section will display the overall accessibility score.
- You can select a specific test result to view detailed information.
- Below the score, a data frame will show all the issues found.
- You can download the JSON or CSV reports using the download functionality.

## Troubleshooting

If you encounter any issues with the URL crawling, ensure that the website is accessible and that you have a stable internet connection. For issues with the accessibility tests, check the console for any error messages that can provide more context.

## Contributing

Contributions to the Web Accessibility Checker are welcome! Please read our contributing guidelines for details on how to submit changes and how to build and test your changes to the project.

## License

This project is licensed under the MIT License.

## Contact

For support or any queries, please reach out to support@example.com.