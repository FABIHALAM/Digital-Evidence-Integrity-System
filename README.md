# DEIS X - Digital Evidence Integrity System

A comprehensive digital forensics platform for evidence management and integrity verification.

## Features

- **Blockchain-based Integrity**: Ensures evidence integrity using cryptographic hashing and blockchain technology.
- **User Management**: Role-based access control with admin, investigator, and viewer roles.
- **File Analysis**: Deep analysis including metadata extraction, anomaly detection, and VirusTotal integration.
- **QR Code Generation**: Generate QR codes for easy case reference.
- **PDF Reports**: Export forensic reports in PDF format.
- **Two-Factor Authentication**: Enhanced security with 2FA support.
- **Rate Limiting**: Protection against brute-force attacks.
- **Email Notifications**: Password reset and notification system.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/deis-x.git
   cd deis-x
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## Usage

- Access the web interface at `http://localhost:5000`
- Register a new account or login with existing credentials
- Upload files for analysis and case creation
- Verify file integrity using the verification endpoints

## Technologies Used

- **Backend**: Flask, SQLAlchemy, Celery
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (configurable to PostgreSQL/MySQL)
- **Security**: Flask-Talisman, Flask-Limiter, bcrypt
- **AI/ML**: Google Gemini for anomaly detection
- **Other**: PyQt5 for GUI, ReportLab for PDFs, Redis for caching

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and research purposes. Ensure compliance with local laws and regulations when handling digital evidence.
