
# SAREP Dashboard Redesign Walkthrough

I have redesigned the SAREP Dashboard to match the requested mockup and improved the internal architecture.

## 🏗 Architecture Changes

The monolithic `app.py` has been refactored into a modular structure:

- **`app/app.py`**: Main entry point. Handles the UI layout, navigation, and state management.
- **`app/utils.py`**: Contains core logic, model loading, and risk calculation functions.
- **`app/data.py`**: Generates mock student data for the "Lista Priorizada" view.
- **`app/styles.py`**: Centralizes all CSS styles, including the new card designs and risk indicators.

## 🎨 Design Updates

### 1. Sidebar Navigation

- Implemented a clean sidebar with navigation options (Dashboard, Estudiantes, etc.).
- Matches the dark sidebar style from the mockup.

### 2. Dashboard Layout

- **Left Column ("Lista Priorizada")**:
  - Displays a list of students sorted by risk score.
  - Each item shows the avatar, name, and risk percentage.
  - Click "Ver Perfil" to load the student's details.
- **Right Column ("Student Profile")**:
  - **Header**: Displays student avatar, name, email, and key stats.
  - **Risk Circle**: A visual SVG-based circle indicating the risk score, matching the mockup.
  - **Academic Data**: An interactive form that allows you to modify the student's academic performance (S2 Approved/Enrolled) to simulate changes in risk.
  - **Risk Diagnosis**: A highlighted box showing the "Riesgo Principal" and a description.
  - **Intervention**: Suggested actions and an "Agendar sesión" button.

## 🚀 How to Run

Run the app using the same command as before:

```bash
streamlit run app/app.py
```

## 📸 Features

- **Interactive Simulation**: Even though it looks like a static dashboard, the "Academic Data" section is fully interactive. Changing the values updates the risk score in real-time using the XGBoost model.
- **Contextual Logic**: The "Riesgo Principal" is derived from the student's contextual data (Satisfaction, Economic Challenge, etc.) using the logic defined in `utils.py`.
