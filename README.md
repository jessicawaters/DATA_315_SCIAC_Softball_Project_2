# SCIAC Softball Data Wrangling and Dashboard Project

## Project Overview

This project analyzes SCIAC (Southern California Intercollegiate Athletic Conference) softball data spanning the 2019–2025 seasons. The dataset was constructed by scraping game schedules and results from official athletic websites and then cleaning and organizing the data for analysis and visualization.

The primary objective of this project is to examine team performance trends, compare programs within the conference, and explore potential relationships between athletic success and institutional or program-level factors such as coaching stability, scoring performance, enrollment, and tuition.

The final product is an interactive Streamlit dashboard that allows users to explore team statistics, head-to-head matchups, and broader conference-level insights.

---

## Data Source

The dataset was collected from SCIAC softball team websites and includes game-level records across multiple seasons. The raw data was processed into structured formats for analysis.

The following datasets are included in this project:

- `clean_softball_data.csv`
- `softball_data.csv`
- `team_summary.csv`

These files contain game-level information, aggregated team statistics, and institutional attributes.

---

## Intended Audience

This project is designed for multiple potential audiences:

- Coaches and athletic staff interested in evaluating team performance and opponent trends
- Sports analysts studying competitive balance and performance patterns
- Prospective student-athletes seeking to understand program competitiveness
- Researchers analyzing relationships between institutional characteristics and athletic outcomes

---

## Data Cleaning and Validation

Several data cleaning and validation steps were applied to ensure accuracy and consistency:

- Converted game dates to standardized datetime format
- Removed records with missing or invalid year values
- Standardized team naming conventions across all datasets
- Removed duplicate game entries using a composite key of team, opponent, and date
- Verified that win indicators were binary and consistently formatted
- Handled missing values in key numeric and categorical fields

These steps ensured that the dataset was reliable for both analysis and visualization.

---

## Exploratory Data Analysis and Visualizations

The project includes multiple visualizations created using Plotly and Streamlit. These visualizations are designed to support both descriptive analysis and comparative insights.

Key visualizations include:

- Team win percentage trends over time
- Geographic distribution of programs using a map visualization
- Offensive and defensive performance comparisons
- Conference versus non-conference performance analysis
- Coaching stability versus win percentage relationships
- Enrollment and tuition versus athletic success
- Program momentum over time
- Head-to-head matchup comparisons between teams

At least one visualization includes a geographic map, and all visualizations are interactive.

---

## Dashboard Features

An interactive Streamlit dashboard was developed to support exploration of the dataset.

### Interactive Components

- Team selection (single or comparative mode)
- Year-based filtering of performance data
- Tab-based navigation for different analysis sections
- Dataset selection viewer for raw and cleaned data
- Dynamic head-to-head matchup filtering

### Dashboard Sections

- Team Explorer: Individual team performance analysis
- Head-to-Head Comparison: Direct comparison between two teams
- Conference Insights: Broader program and conference trends
- Dataset Viewer: Access to raw and processed data

---

## Tools and Technologies

- Python
- Pandas
- NumPy
- Plotly
- Streamlit
- Jupyter Notebook
- Git and GitHub
