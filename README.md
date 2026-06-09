# Edo State Government Performance Appraisal System

A comprehensive Flask-based web application for managing employee performance appraisals for the Edo State Government Civil Service Commission.

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)
- [Test Users](#test-users)
- [Workflow Guide](#workflow-guide)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## 🎯 System Overview

The system manages two distinct performance appraisal modules:

### Leg 1: Gen 79A Annual Performance Appraisal
- Traditional single annual report
- Two-level approval workflow (Reporting Officer → Countersigning Officer)
- A-F grading scale with numerical equivalents
- QR code verification for report authenticity
- PDF generation with Edo State Government branding

### Leg 2: Quarterly Performance Appraisal System
- Continuous performance tracking across 4 quarters
- SMART goal setting and approval workflow
- End-of-year appraisal with 0-80 scoring system
- Three-level workflow (Officer → Reporting Officer → Countersigning Officer)
- Officer response mechanism for assessment disagreements

## ✨ Features

- **Authentication & Authorization**: Role-based access control (Admin, Officer, Reporting Officer, Countersigning Officer, HR)
- **Report Management**: Create, edit, submit, and track performance reports
- **Workflow Engine**: Automated routing through approval chains
- **Audit Trail**: Comprehensive logging of all system actions
- **PDF Generation**: Professional report export with QR codes
- **Admin Dashboard**: Full control over users, reports, and system settings
- **Background Logo Settings**: Customizable watermark logo
- **Bulk User Upload**: CSV import for user management
- **Email Notifications**: (Configured separately)

## 📂 Project Structure
