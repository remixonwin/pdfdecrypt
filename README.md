# Minnesota Driver's License Quiz Application

An interactive, adaptive quiz application designed to help users prepare for their Minnesota driver's license test. Built with Python and Streamlit, this application provides a comprehensive learning experience with real-time feedback and progress tracking.

## 🚗 Features

- **Comprehensive Question Bank**: Over 200 carefully curated questions covering all aspects of Minnesota driving laws and regulations
- **Adaptive Learning**: Questions that haven't been answered correctly are prioritized in future sessions
- **Progress Tracking**: Persistent progress tracking across sessions
- **Interactive UI**: Clean, modern interface with immediate feedback
- **Detailed Explanations**: Comprehensive explanations for each answer
- **Performance Analytics**: Track your progress and identify areas for improvement
- **Mobile-Friendly**: Responsive design that works on all devices
- **Error Reporting**: Built-in system to report unclear or incorrect questions

## 🛠️ Technical Features

- Written in Python 3.12
- Built with Streamlit for the web interface
- CSV-based question bank for easy updates
- JSON-based progress tracking
- Comprehensive error logging
- Modular code structure
- Custom CSS styling

## 📋 Prerequisites

- Python 3.12 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

## 🚀 Installation

1. Clone the repository (or download the ZIP file):
   ```bash
   git clone https://github.com/yourusername/minnesota-drivers-quiz.git
   cd minnesota-drivers-quiz
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   .\venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Running the Application

1. Start the application:
   ```bash
   streamlit run streamlit_app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:8501
   ```

## 📱 Using the Application

1. **Start Quiz**: Begin a new quiz session
2. **Answer Questions**: Select your answer and get immediate feedback
3. **View Explanations**: Read detailed explanations for each answer
4. **Track Progress**: Monitor your performance over time
5. **Report Issues**: Use the built-in reporting system for any concerns

## 🔧 Configuration

The application can be configured through the following files:
- `Minnesota_Driving_Quiz.csv`: Question bank
- `config.json`: Application settings
- `.streamlit/config.toml`: Streamlit configuration

## 📊 Features in Detail

### Question Types
- Multiple choice questions
- True/False questions
- Scenario-based questions
- Traffic sign identification

### Progress Tracking
- Session scores
- Overall progress
- Weak areas identification
- Performance trends

### User Experience
- Clean, intuitive interface
- Mobile-responsive design
- Immediate feedback
- Detailed explanations
- Progress visualization

## 🤝 Contributing

We welcome contributions! Please feel free to:
1. Report bugs
2. Suggest new features
3. Submit pull requests
4. Add new questions
5. Improve documentation

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Minnesota Department of Public Safety
- Driver and Vehicle Services Division
- Open-source community

## 📞 Support

For support:
1. Check the FAQ section
2. Use the built-in error reporting
3. Open an issue on GitHub
4. Contact the maintainers

## 🔄 Updates

The question bank is regularly updated to reflect the latest Minnesota driving laws and regulations. Check back regularly for updates!
