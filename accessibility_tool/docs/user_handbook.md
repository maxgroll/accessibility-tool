# User Handbook for Web Accessibility Checker

Welcome to the User Handbook for the Web Accessibility Checker. This guide will help you understand how to use the application effectively to assess and improve the accessibility of websites.

## Getting Started

### Installation

To use the Web Accessibility Checker, follow these steps:

1. Clone the repository from GitHub.
2. Ensure Python is installed on your system.
3. Navigate to the project directory.
4. Install the required packages: `pip install -r requirements.txt`.
5. Launch the application: `streamlit run web_accessibility_checker.py`.

### Interface Overview

The application features a simple and user-friendly interface, consisting of the following sections:

- **URL Input**: Where you enter the website's URL for accessibility testing.
- **Crawl Depth Setting**: To determine the depth of URL crawling.
- **Test Type Selection**: To choose the type of accessibility test.
- **Results Display**: To view the accessibility scores and issue details.
- **Report Download**: To download detailed reports.

## Using the Application

### Finding URLs

1. Enter the base URL of the website in the URL input field.
2. Set the desired crawl depth.
3. Click "Find URLs" to initiate the crawling process.

### Selecting Test Type

1. Choose the type of test: "Test only homepage," "Test all URLs," or "Select specific URLs."
2. For specific URL tests, select the URLs from the multi-select box.
3. Confirm your selection to proceed.

### Running Tests

1. Click "Run Accessibility Tests" to start testing the selected URLs.

### Viewing Results

1. After testing, the overall accessibility score will be displayed.
2. Select a specific test result to view detailed information.
3. The data frame will show all issues found.
4. Download JSON or CSV reports using the download functionality.

## Troubleshooting

- **Crawling Issues**: Ensure the website is accessible and check your internet connection.
- **Testing Issues**: Check for error messages in the console for more context.

## Contributing

Your contributions to enhance the application are welcome! Please follow our guidelines for submitting changes.

## License

The Web Accessibility Checker is licensed under the MIT License.

## Contact

For support or queries, please contact us at support@example.com.