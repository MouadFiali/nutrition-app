# Nutrition App

A comprehensive web application for nutrition tracking, meal planning, and dietary adherence analysis.

![Nutrition App](https://img.shields.io/badge/Nutrition-App-green)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.42.1-red)

## Overview

Nutrition App is a feature-rich application designed to help users manage their nutrition, create meal plans, and track their dietary progress. The app provides a complete solution for:

- Profile management with personalized nutrition targets
- Food library with nutritional information
- Meal creation and management (both custom and ingredient-based)
- Meal program planning for days or weeks
- Meal tracking and logging
- Progress visualization and reporting
- Program adherence analysis

## Motivation

While there are numerous mobile applications for nutrition tracking, quality web-based solutions are surprisingly rare in this field. Most existing web platforms either offer limited features or require paid subscriptions to unlock full functionality. Additionally, many lack an intuitive user interface and visual appeal.

This project was born from a desire to create a comprehensive nutrition tracking and meal planning platform that:

- Provides a **desktop-first experience** for users who prefer working on PCs rather than mobile devices
- Offers **complete functionality**
- Prioritizes **user experience and visual design**
- Allows for **greater flexibility in meal planning and tracking** than existing solutions

The application is designed to be user-friendly and visually appealing, making nutrition management more engaging and less of a chore.

## Features

- **Profile Management**: Track weight, height, age, gender, activity level, and nutritional goals
- **Food Database**: Create and manage your personal food library with detailed nutrition information
- **Meal Builder**: Create meals by combining foods from your database or add custom meals with known macros
- **Meal Programs**: Schedule meals for specific days and meal times
- **Meal Tracking**: Log your actual meals and compare them to your plan
- **Progress Analysis**: Visualize your nutrition intake and adherence to your plan
- **Program Adherence**: Analyze how closely you follow your meal plans with detailed comparisons

## Requirements

- Python 3.9 or higher
- Dependencies listed in `requirements.txt`

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/MouadFiali/nutrition-app.git
cd nutrition-app
```

### 2. Create a Virtual Environment (Optional but Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
streamlit run streamlit_app.py
```

The application will start and open in your default web browser at `http://localhost:8501`.

## Getting Started

1. **Set Up Your Profile**: First, create your profile with personal metrics and goals
2. **Add Food Sources**: Build your food database with your commonly eaten foods
3. **Create Meals**: Combine foods into meals or add custom meals
4. **Plan Your Meals**: Create meal programs for specific time periods
5. **Track Your Progress**: Log what you actually eat and monitor your nutrition
6. **Analyze Adherence**: Compare your planned meals with your actual consumption

## Test Data

The repository includes sample test data to help you get started quickly. You can find it in the `tests` folder along with a README file explaining how to use the data to populate your database.

To use the test data, read the instructions in `tests/README.md`. This will allow you to explore the application with pre-populated data, giving you a feel for how the app works without having to manually enter everything.

## Database

The application uses SQLite for data storage. The database file is created automatically when the application runs for the first time.

## Development Notes

This application was developed using an AI-assisted approach:

- Approximately 90% of the codebase was generated through AI interactions, using precise and thoughtful prompting
- The core ideas, feature set, and application flow were human-designed, with AI assistance in refining and expanding concepts
- Manual debugging and fine-tuning were periodically required to address specific issues and improve user experience
- The architecture and design decisions were guided by human oversight while leveraging AI for implementation details

This approach demonstrates how effective collaboration between human creativity and AI assistance can produce sophisticated applications efficiently. The development process focused on creating a tool that genuinely solves user needs while maintaining high standards for code quality and user experience.

Another note: This README file was also generated using AI in case you are wondering 😄.

One last note: As the app was developed using AI, it might contain some bugs or issues that weren't tested properly (especially in the comparison or calculation parts). Please report any inconsistencies you find.