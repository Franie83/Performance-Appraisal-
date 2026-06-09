I'll save the documentation to your project directory. Here's how to create the README file:

```batch
notepad README_QUARTERLY_APPRAISAL.md
```

Copy and paste the complete documentation below:

```markdown
# Quarterly Performance Appraisal System - Complete Documentation

## System Overview

The Quarterly Performance Appraisal System (Leg 2) is a comprehensive performance management system that tracks employee performance throughout the year with quarterly reviews and end-of-year assessment. Unlike the Gen 79A annual appraisal, this system focuses on continuous performance monitoring with SMART goal setting and regular feedback.

---

## Complete Workflow Flowchart

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    QUARTERLY PERFORMANCE APPRAISAL WORKFLOW                  │
└─────────────────────────────────────────────────────────────────────────────┘

                                    START
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  STEP 1: PLANNING (Jan 2-5)         │
                    │  Owner: OFFICER                      │
                    │  • Officer sets SMART goals         │
                    │  • Lists goals in priority order    │
                    │  • Submits plan to Reporting Officer │
                    └─────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  STEP 2: APPROVAL (Jan 2-10)        │
                    │  Owner: REPORTING OFFICER            │
                    │  • Reviews goals                    │
                    │  • Approves OR requests modifications│
                    └─────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  STEP 3-4: QUARTER 1 REVIEW         │
                    │  (Apr 1-8)                          │
                    │  Owner: OFFICER → REPORTING OFFICER  │
                    │  • Officer reports achievements     │
                    │  • Reporting Officer reviews        │
                    │  • Provides directives              │
                    └─────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  STEPS 5-6: QUARTER 2 REVIEW        │
                    │  (Jul 1-8)                          │
                    │  Owner: OFFICER → REPORTING OFFICER  │
                    │  • Repeat Q1 process                │
                    └─────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  STEPS 7-8: QUARTER 3 REVIEW        │
                    │  (Oct 1-8)                          │
                    │  Owner: OFFICER → REPORTING OFFICER  │
                    │  • Repeat Q1 process                │
                    └─────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  STEP 9-10: END OF YEAR APPRAISAL   │
                    │  (Dec 15-22)                        │
                    │  Owner: OFFICER → REPORTING OFFICER  │
                    │  • Officer submits annual report    │
                    │  • Reporting Officer assesses       │
                    │  • System auto-calculates scores    │
                    └─────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  STEP 11: OFFICER RESPONSE          │
                    │  Owner: OFFICER                      │
                    │  • Agrees or disagrees with assessment│
                    │  • Provides reasons if disagrees     │
                    └─────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  STEP 12: FINAL REVIEW              │
                    │  Owner: PERMANENT SECRETARY          │
                    │  • Reviews assessment               │
                    │  • May adjust ratings               │
                    │  • Finalizes appraisal              │
                    └─────────────────────────────────────┘
                                      │
                                      ▼
                                    FINISH
```

---

## Role Definitions & Responsibilities

### 1. OFFICER (Regular Staff)
| Responsibility | Actions |
|----------------|---------|
| Goal Setting | Creates SMART goals for each quarter |
| Quarterly Review | Reports achievements, challenges, and recovery plans |
| Yearly Appraisal | Submits annual report and responds to assessment |
| Disagreement | Can dispute assessment with reasons |

### 2. REPORTING OFFICER (Supervisor/Line Manager)
| Responsibility | Actions |
|----------------|---------|
| Goal Approval | Approves or requests modifications to goals |
| Quarterly Assessment | Reviews officer's performance each quarter |
| Yearly Evaluation | Rates officer on 10 performance criteria (1-5 scale) |
| Feedback | Provides comments and directives |

### 3. PERMANENT SECRETARY / HEAD OF AGENCY
| Responsibility | Actions |
|----------------|---------|
| Final Review | Reviews assessment when officer disagrees |
| Score Adjustment | Can adjust ratings if necessary |
| Finalization | Approves and finalizes the appraisal |

---

## Database Schema

### quarterly_goals Table
```sql
CREATE TABLE quarterly_goals (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,           -- Officer's user ID
    planning_year INTEGER NOT NULL,      -- Year of the plan
    quarter INTEGER NOT NULL,            -- 1, 2, 3, or 4
    goal_description TEXT NOT NULL,      -- SMART goal description
    priority INTEGER DEFAULT 1,          -- 1=Highest to 5=Lowest
    success_criteria TEXT,               -- How to measure success
    
    -- Planning Phase
    plan_status VARCHAR(50) DEFAULT 'DRAFT',
    plan_submitted_at DATETIME,
    plan_approved_at DATETIME,
    plan_approved_by INTEGER,            -- Reporting Officer ID
    plan_modifications TEXT,              -- Changes requested
    
    -- Review Phase
    review_status VARCHAR(50) DEFAULT 'PENDING',
    achievements TEXT,                    -- What was accomplished
    challenges TEXT,                      -- What difficulties faced
    reasons_for_failure TEXT,             -- Explanation for underperformance
    recovery_plan TEXT,                   -- Plan to get back on track
    
    -- Reporting Officer's Feedback
    reporting_officer_comments TEXT,
    further_directives TEXT,
    quarter_2_adjustments TEXT,           -- Adjustments for next quarter
    review_completed_at DATETIME,
    review_completed_by INTEGER,          -- Reporting Officer ID
    
    created_at DATETIME,
    updated_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (plan_approved_by) REFERENCES users(id),
    FOREIGN KEY (review_completed_by) REFERENCES users(id)
);
```

### yearly_appraisals Table
```sql
CREATE TABLE yearly_appraisals (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,             -- Officer's user ID
    appraisal_year INTEGER NOT NULL,       -- Year of appraisal
    annual_report TEXT,                   -- Officer's yearly report
    reasons_for_failure TEXT,              -- Explanations for underperformance
    submitted_at DATETIME,
    
    -- SECTION A: Automated Assessments (0-10 points each)
    training_attendance_score INTEGER DEFAULT 0,  -- From JOOPSA
    clock_in_score INTEGER DEFAULT 0,             -- From HRM
    peer_review_score INTEGER DEFAULT 0,          -- 360 review
    
    -- SECTION B: Reporting Officer's Assessment (1-5 scale)
    diligently_executed INTEGER DEFAULT 3,
    delivered_timelines INTEGER DEFAULT 3,
    punctuality_effectiveness INTEGER DEFAULT 3,
    decency_presentability INTEGER DEFAULT 3,
    productivity INTEGER DEFAULT 3,
    communication_skills INTEGER DEFAULT 3,
    team_collaboration INTEGER DEFAULT 3,
    independent_work INTEGER DEFAULT 3,
    openness_to_learning INTEGER DEFAULT 3,
    proactivity_initiative INTEGER DEFAULT 3,
    
    section_b_total INTEGER DEFAULT 0,    -- Auto-calculated sum
    
    reporting_officer_comments TEXT,
    reporting_officer_sent_at DATETIME,
    
    -- Officer's Response
    officer_agrees BOOLEAN DEFAULT TRUE,
    officer_disagreement_reason TEXT,
    officer_response_at DATETIME,
    
    -- Permanent Secretary Review
    ps_review_completed BOOLEAN DEFAULT FALSE,
    ps_review_date DATETIME,
    ps_comments TEXT,
    
    -- Status Tracking
    status VARCHAR(50) DEFAULT 'DRAFT',
    finalized_at DATETIME,
    
    reporting_officer_id INTEGER,
    permanent_secretary_id INTEGER,
    
    created_at DATETIME,
    updated_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (reporting_officer_id) REFERENCES users(id),
    FOREIGN KEY (permanent_secretary_id) REFERENCES users(id)
);
```

---

## Status Flow Diagram

### Goal Status Flow
```
DRAFT → SUBMITTED → (APPROVED or MODIFIED)
                         ↓
                    MODIFIED → (Officer edits and resubmits)
                         ↓
                    APPROVED → Ready for Quarterly Review
```

### Review Status Flow
```
PENDING → SUBMITTED (Officer submits quarterly report)
              ↓
         REVIEWED (Reporting Officer completes review)
              ↓
         COMPLETED (Ready for next quarter)
```

### Yearly Appraisal Status Flow
```
DRAFT → SUBMITTED (Officer submits)
           ↓
      RO_REVIEW (Reporting Officer assesses)
           ↓
      OFFICER_RESPONSE (Officer responds)
           ↓
      PS_REVIEW (Permanent Secretary reviews - if disagreement)
           ↓
      FINALIZED (Appraisal completed)
```

---

## Scoring System

### Section A: Automated Assessments (Max 30 points)

| Source | Score Range | Description |
|--------|-------------|-------------|
| Training Attendance (JOOPSA) | 0-10 | Based on mandatory training completion |
| Clock-in Report (HRM) | 0-10 | Based on punctuality and attendance records |
| 360 Peer Review | 0-10 | Colleague feedback and assessment |

### Section B: Reporting Officer Assessment (Max 50 points)

Each criterion rated 1-5:

| Rating | Description |
|--------|-------------|
| 5 | Outstanding - Exceeds expectations significantly |
| 4 | Very Good - Consistently exceeds expectations |
| 3 | Good - Meets expectations consistently |
| 2 | Fair - Sometimes meets expectations |
| 1 | Poor - Frequently fails to meet expectations |

**Assessment Criteria:**

| # | Criterion |
|---|-----------|
| 1 | Officer diligently executed all tasks |
| 2 | Delivered tasks within agreed timelines |
| 3 | Punctual and contributed effectively |
| 4 | Decent and presentable appearance |
| 5 | Highly productive |
| 6 | Good communication skills |
| 7 | Collaborated well with team |
| 8 | Can work independently |
| 9 | Open to criticism and willing to learn |
| 10 | Proactive and uses initiative |

### Total Score Calculation

```
Total Score = Section A (0-30) + Section B (0-50) = 0-80 points
```

### Rating Scale

| Score Range | Rating | Description |
|-------------|--------|-------------|
| 70-80 | Outstanding | Exceptional performer |
| 60-69 | Very Good | Strong performer |
| 50-59 | Good | Satisfactory performer |
| 40-49 | Fair | Needs improvement |
| 0-39 | Poor | Significant improvement needed |

---

## User Roles & Permissions Matrix

| Action | OFFICER | REPORTING OFFICER | PERMANENT SECRETARY | ADMIN |
|--------|---------|-------------------|---------------------|-------|
| Create/Edit Goals | ✅ | ❌ | ❌ | ✅ |
| Submit Goals for Approval | ✅ | ❌ | ❌ | ✅ |
| Approve/Modify Goals | ❌ | ✅ | ❌ | ✅ |
| Submit Quarterly Review | ✅ | ❌ | ❌ | ✅ |
| Review Quarterly Report | ❌ | ✅ | ❌ | ✅ |
| Submit Yearly Appraisal | ✅ | ❌ | ❌ | ✅ |
| Assess Yearly Appraisal | ❌ | ✅ | ❌ | ✅ |
| Respond to Assessment | ✅ | ❌ | ❌ | ✅ |
| Final Review & Adjust | ❌ | ❌ | ✅ | ✅ |
| View All Reports | ❌ | ❌ | ❌ | ✅ |
| Download PDF | ✅ | ✅ | ✅ | ✅ |
| Manage Users | ❌ | ❌ | ❌ | ✅ |

---

## Timeline/Deadlines

| Period | Activity | Responsible |
|--------|----------|-------------|
| **January 2-5** | Goal Setting & Planning | Officer |
| **January 2-10** | Goal Approval | Reporting Officer |
| **April 1-5** | Quarter 1 Review Submission | Officer |
| **April 1-8** | Quarter 1 Review & Directives | Reporting Officer |
| **July 1-5** | Quarter 2 Review Submission | Officer |
| **July 1-8** | Quarter 2 Review & Directives | Reporting Officer |
| **October 1-5** | Quarter 3 Review Submission | Officer |
| **October 1-8** | Quarter 3 Review & Directives | Reporting Officer |
| **December 15-22** | End of Year Appraisal | Officer → Reporting Officer |
| **December 23-28** | Officer Response | Officer |
| **December 29-31** | Final Review & Finalization | Permanent Secretary |

---

## File Structure

```
performance_appraisal/
├── app/
│   ├── models/
│   │   ├── quarterly_plan.py           # Quarterly goals model
│   │   └── system_settings.py          # System configuration
│   ├── quarterly/
│   │   ├── __init__.py                 # Blueprint definition
│   │   └── routes.py                   # All quarterly routes
│   ├── templates/
│   │   └── quarterly/
│   │       ├── dashboard.html          # Main quarterly dashboard
│   │       ├── plan_goal.html          # Create/edit goals
│   │       ├── approve_goal.html       # Approve/modify goals
│   │       ├── quarterly_review.html   # Submit quarterly review
│   │       ├── review_quarterly.html   # Review quarterly report
│   │       ├── yearly_appraisal.html   # Officer's yearly report
│   │       ├── ro_yearly_appraisal.html# Reporting Officer assessment
│   │       ├── respond_appraisal.html  # Officer's response
│   │       └── ps_review.html          # Permanent Secretary review
│   └── utils/
│       └── pdf_quarterly.py            # PDF generation
└── instance/
    └── appraisal.db                    # SQLite database
```

---

## API Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/quarterly/dashboard` | Main dashboard | All |
| GET | `/quarterly/plan-goal` | Create goal form | Officer/Admin |
| POST | `/quarterly/plan-goal` | Save goal | Officer/Admin |
| POST | `/quarterly/submit-goal/<id>` | Submit for approval | Officer/Admin |
| GET | `/quarterly/approve-goal/<id>` | Approval form | Reporting Officer/Admin |
| POST | `/quarterly/approve-goal/<id>` | Process approval | Reporting Officer/Admin |
| GET | `/quarterly/quarterly-review/<quarter>` | Review form | Officer/Admin |
| POST | `/quarterly/quarterly-review/<quarter>` | Submit review | Officer/Admin |
| GET | `/quarterly/review-quarterly/<id>` | Review form | Reporting Officer/Admin |
| POST | `/quarterly/review-quarterly/<id>` | Submit review | Reporting Officer/Admin |
| GET | `/quarterly/yearly-appraisal` | Yearly appraisal form | Officer/Admin |
| POST | `/quarterly/yearly-appraisal` | Submit yearly report | Officer/Admin |
| GET | `/quarterly/ro-yearly-appraisal/<id>` | RO assessment form | Reporting Officer/Admin |
| POST | `/quarterly/ro-yearly-appraisal/<id>` | Submit assessment | Reporting Officer/Admin |
| GET | `/quarterly/respond-appraisal/<id>` | Officer response form | Officer/Admin |
| POST | `/quarterly/respond-appraisal/<id>` | Submit response | Officer/Admin |
| GET | `/quarterly/ps-review/<id>` | PS review form | PS/Admin |
| POST | `/quarterly/ps-review/<id>` | Finalize appraisal | PS/Admin |
| GET | `/quarterly/export-pdf/<id>` | Download PDF | All with access |

---

## Installation & Setup

### 1. Database Migration
```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 2. Create Required Users
```bash
python create_users_fixed.py
```

### 3. Assign Roles
- Admin: `admin` / `admin123`
- Reporting Officer: `reporting_officer` / `password123`
- Countersigning Officer: `countersigning_officer` / `password123`
- Regular Officers: `john_doe`, `jane_smith` / `password123`
- HR Officer: `hr_officer` / `password123`

### 4. Configure Permanent Secretary
```bash
python -c "from app import create_app, db; from app.models.user import User; app = create_app(); app.app_context().push(); ps = User(username='permanent_secretary', email='ps@example.com', role='PERMANENT_SECRETARY', is_active=True); ps.set_password('ps123'); db.session.add(ps); db.session.commit(); print('Permanent Secretary created')"
```

---

## Testing Workflow

### Complete Test Scenario

1. **Login as Officer (john_doe)**
   - Create goals for Quarter 1
   - Submit for approval

2. **Login as Reporting Officer**
   - Approve/modify goals
   - Wait for quarterly review

3. **Login as Officer**
   - Submit Quarter 1 review
   - Report achievements/challenges

4. **Login as Reporting Officer**
   - Review Quarter 1 report
   - Provide directives

5. **Repeat for Quarters 2 & 3**

6. **Login as Officer**
   - Submit Yearly Appraisal

7. **Login as Reporting Officer**
   - Complete Section A & B assessment
   - Send to officer

8. **Login as Officer**
   - Respond (agree/disagree)

9. **Login as Permanent Secretary** (if disagreement)
   - Review and finalize

10. **Download PDF Report**

---

## Common Issues & Troubleshooting

| Issue | Solution |
|-------|----------|
| Goals not showing for Reporting Officer | Ensure user has REPORTING_OFFICER role |
| Can't submit quarterly review | Create goals for that quarter first |
| Yearly appraisal not appearing | Check that appraisal_year is current |
| PDF generation fails | Ensure reportlab is installed: `pip install reportlab` |
| Scores not calculating | Verify all ratings are between 1-5 |

---

## Support & Maintenance

- **Database Backups**: Regular backups of `instance/appraisal.db`
- **Log Files**: Check Flask console for errors
- **User Management**: Admin can manage all users and roles
- **PDF Templates**: Customize in `app/utils/pdf_quarterly.py`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024 | Initial release of Quarterly Performance Appraisal System |

---

This documentation covers the complete Quarterly Performance Appraisal System (Leg 2). The system is fully integrated with the existing Gen 79A system but operates independently with its own workflow, scoring, and approval hierarchy.
```

## Save and verify the file was created:

```batch
dir README_QUARTERLY_APPRAISAL.md
```

The documentation has been saved to your project directory as `README_QUARTERLY_APPRAISAL.md`. You can open it with any text editor or Markdown viewer.