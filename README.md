# StudyStar

![StudyStar mockup image](/readme-files/studystar_devices_mockup.png)

StudyStar is a web-based study tracker designed to help learners plan, track, and reflect on their educational progress. The platform allows users to create courses, set personalised goals, log study sessions, and visualise their progress through clean, data-driven charts. StudyStar supports learners in building consistent study habits while offering a clear overview of their workload and achievements.

Users can log a study session by selecting a course, adding a duration, optional notes, and choosing a date and time. StudyStar then aggregates all study data to display helpful insights, including progress toward goals, total hours completed, weekly streaks, and motivational milestones.

A space-themed achievement system rewards users for key milestones such as hitting hour targets, completing goals, and maintaining weekly streaks - helping learners stay motivated throughout their study journey.

Instructions are provided throughout the platform to guide users, and authenticated users can view, edit, or delete their courses, goals, and sessions. A dedicated contact page allows users to send questions, feedback, or suggestions directly through the app.

Visit the deployed website [here](https://studystar-tracker-4c939321ffcd.herokuapp.com/).

## Table of Contents

- [User Experience (UX)](#user-experience-ux)
    - [Project Goals](#project-goals)
- [User Goals](#user-goals)
- [Structure](#structure)
- [Entity Relationship Diagram](#entity-relationship-diagram)
- [Wireframes](#wireframes)
- [Colour Scheme](#colour-scheme)
- [Typography](#typography)
- [Features](#features)
    - [General](#general)
    - [Home Page](#home-page)
    - [Dashboard](#dashboard) 
    - [Courses](#courses)
    - [Goals](#goals)
    - [Study Sessions](#study-sessions)
    - [Achievements](#achievements)
    - [Contact](#contacts)
    - [User Accounts](#user-accounts)
- [Technologies Used](#technologies-used)
    - [Languages Used](#languages-used)
    - [Libraries and Frameworks](#libraries-frameworks)
    - [Django Packages and Dependencies](#django-packages-dependencies)
    - [Database Management](#database-management)
    - [Tools and Programs](#tools-programmes)
- [Testing](#testing)
- [Deployment](#deployment)
    - [Deploying on Heroku](#deploying-on-heroku)
- [Finished Product](#finished-product)
- [Reflections](#reflections) 
    - [Future Features](#future-features)
- [Credits](#credits)
    - [Content](#content)
    - [Media](#media)

## User Experience (UX)

### Project Goals

StudyStar is designed to deliver a clean, intuitive experience that helps users take control of their learning. The primary project goals are:

- Provide a structured way for users to create and manage courses.
- Allow users to set weekly or long-term study goals with clear progress tracking.
- Enable fast, simple logging of study sessions with optional notes and timestamps.
- Offer meaningful data visualisation using Chart.js, including weekly progress, streaks, and long-term trends.
- Reward user progress through a fun achievement system with space-themed badges.
- Require user authentication for all course, goal, and session management, tying all data to the correct user.
- Provide a responsive, mobile-first interface for tracking progress on any device.
- Offer a clean contact form so users can ask questions or provide suggestions.

## User Goals

1. **Create and manage courses**
    * As a Site User I want to add and edit my courses so that I can organise the subjects or topics I’m currently studying.

2. **Set personalised study goals**
    * As a Site User I want to define weekly or long-term goals so that I have clear targets to work towards.

3. **Log study sessions quickly**
    * As a Site User I want to record my study duration, notes, and course selection so that I can keep an accurate track of my learning.

4. **View my study progress**
    * As a Site User I want to see my logged hours, completed lessons, and overall progress so that I can understand how I’m doing.

5. **Track trends and streaks**
    * As a Site User I want to view charts showing my weekly progress and streaks so that I can stay motivated and maintain consistency.

6. **Earn achievements**
    * As a Site User I want to earn badges for milestones like completed goals or study streaks so that I feel rewarded for my efforts.

7. **Edit or delete my data**
    * As a Site User I want to update or remove courses, goals, or sessions so that I can keep my records accurate.

8. **Access the app on any device**
    * As a Site User I want the website to work on both desktop and mobile so that I can log sessions wherever I study.

9. **Use a secure, account-based system**
    * As a Site User I want my study data to be tied to my account so that only I can view and manage it.

10. **Contact the site owner**
    * As a Site User I want to message the site owner so that I can ask questions, share feedback, or make suggestions.

## Structure

The structure of the StudyStar website is shown in the diagram below. After logging in, users land on the dashboard, which acts as the central hub for accessing their courses, goals, achievements, and study session tools. From the Courses section, users can view all of their courses, add new ones, or open a course detail page where individual study sessions can be logged directly. The Goals area allows users to track their progress through charts and goal tabs, as well as create new goals. A dedicated Achievements page displays all earned badges to help motivate consistent study habits. Core actions such as adding a course, creating a goal, or logging a session each have their own dedicated form pages. This structure ensures that users can navigate intuitively between their study data, add new information easily, and explore their overall progress with minimal friction.

<img src="./readme-files/studystar-site-map.svg">

Note that:

- The header, footer, and navigation menu are the same
on all pages.
- Logged in users will have a side navigation menu to access user areas.
- Links, buttons and form provide clear feedback to the user.
- Users can add, edit, delete and view their goals and courses.
- Users can delete their logged study sessions.
- There is a custom 404 error page.

## Entity Relationship Diagram

The ERD below was created using [Mermaid](https://www.mermaidchart.com/d/04cf3cfa-1108-454d-9201-8aa6f6211e76).

The relational database is managed by **PostgreSQL**, and the core schema is shown in the entity relationship diagram below.

<img src="./readme-files/erd.svg">

**Course Model**

Represents a course or subject the user is studying. Each course is owned by a specific user and acts as the parent model for related goals and study sessions.

Attributes:

- owner: The user who created the course.
- title: The name of the course.
- description: A text field describing the course.
- start_date: Optional start date for the course.
- end_date: Optional end date for the course.
- status: Indicates whether the course is active, paused, or completed.
- colour: A colour label used for UI categorisation.
- slug: A URL-friendly version of the course title.
- created_at: Timestamp when the course was created.
- updated_at: Timestamp when the course was last updated.

**Goal Model**

Represents a user-defined study goal associated with a specific course. Goals define weekly or long-term targets and track user progress over time.

Attributes:

- user: The user who created the goal.
- course: The course to which the goal belongs.
- weekly_hours_target: Optional weekly hours target.
- weekly_lessons_target: Optional weekly lessons target.
- study_days_per_week: Number of planned study days per week (1–7).
- total_required_lessons: Total lessons required to complete the course.
- milestone_name: A user-defined milestone label (e.g. “Midterm checkpoint”).
- milestone_date: The date of the milestone.
- average_hours_per_less: Average hours per lesson (supports pacing calculations).
- is_active: Indicates whether the goal is currently active.
- created_at: Timestamp when the goal was created.
- updated_at: Timestamp when the goal was last updated.

**GoalOutcome Model**

A weekly snapshot of the user's progress towards a specific goal. Each instance stores calculated progress for one study week, allowing the platform to generate charts and trend insights.

Attributes:

- goal: The goal this outcome belongs to.
- week_start: Start date of the tracked week.
- week_end: End date of the tracked week.
- hours_completed: Total hours studied during that week.
- lessons_completed: Total lessons completed during that week.
- hours_target: Weekly hours target for that specific week.
- lessons_target: Weekly lessons target for that week.
- completed: Indicates whether the weekly target was met.
- notes: Optional notes about the week’s progress.
- created_at: Timestamp when the outcome record was created.
- updated_at: Timestamp when the outcome was last updated.

**StudySession Model**

Represents a single study session logged by the user. Study sessions contribute directly to goal progress and course activity tracking.

Attributes:

- user: The user who logged the study session.
- course: The course associated with the session.
- goal: The goal the session contributes to (optional).
- started_at: The date and time the session began.
- duration_minutes: Duration of the session in minutes.
- notes: Optional text notes about what was studied.

**ContactMessage Model**

Stores messages submitted through the contact form. These messages allow users to ask questions, report issues, or provide feedback.

Attributes:

- user: (Optional) The authenticated user who submitted the message.
- name: The sender’s name.
- email: The sender’s email address.
- message: The body of the message.
- created_at: Timestamp when the message was submitted.

## Wireframes

Wireframes were created using [Balsamiq](https://balsamiq.com/) to plan the design of the web application.

| Page | Desktop | Mobile |
| --- | --- | --- |
| Home | ![Home desktop wireframe](readme-files/home_desktop.png) | ![Home mobile wireframe](readme-files/home_mobile.png) |
| About | ![About desktop wireframe](readme-files/about_desktop.png) | ![About mobile wireframe](readme-files/about_mobile.png) |
| Contact | ![Contact desktop wireframe](readme-files/contact_desktop.png) | ![Contact mobile wireframe](readme-files/contact_mobile.png) |
| Sign In/ Sign Up | ![Sign In / Sign Up desktop wireframe](readme-files/signin_desktop.png) | ![Sign In / Sign Up mobile wireframe](readme-files/signin_mobile.png) |
| Dashboard | ![Dashboard desktop wireframe](readme-files/dashboard_desktop.png) | ![Dashboard mobile wireframe](readme-files/dashboard_mobile.png) |
| Courses | ![Courses desktop wireframe](readme-files/courses_desktop.png) | ![Courses mobile wireframe](readme-files/courses_mobile.png) |
| Goals | ![Goals desktop wireframe](readme-files/goals_desktop.png) | ![Goals mobile wireframe](readme-files/goals_mobile.png) |
| My Sessions | ![My Sessions desktop wireframe](readme-files/sessions_desktop.png) | ![My Sessions mobile wireframe](readme-files/sessions_mobile.png) |

## Colour Scheme

<img alt="Colour scheme image" src="/readme-files/studystar-colour-palette.png">

The StudyStar colour palette is built around a calm yet motivating blend of blues, soft neutrals, and a warm accent shade. The primary colour is Sky Blue (#28AAFF), chosen for its association with clarity, focus, and optimism — qualities that support a productive study environment. This energetic blue also appears in the StudyStar branding, helping to maintain visual consistency across the platform.

To complement the primary blue, a vibrant Periwinkle Blue (#6262FE) is used throughout interactive elements such as buttons and highlights. This secondary blue adds depth to the interface while maintaining a cohesive, modern aesthetic.

A deep Midnight Blue (#252772) provides strong contrast and is used for headings, structural components, and elements that require emphasis without overwhelming the user. Its rich tone reinforces readability and helps anchor the lighter colours in the palette.

The soft off-white Cloud White (#FBF9F9) forms the foundation of the background surfaces, giving the interface a clean and approachable feel. This neutral tone keeps the design airy and ensures that the colourful elements stand out clearly.

Finally, Warm Gold (#ECD363) is used as an accent colour within the achievements system and other celebratory or motivational elements. This golden tone adds a sense of reward and positivity, reinforcing progress and achievement throughout the user experience.

## Typography

StudyStar uses a carefully selected combination of serif and sans-serif typefaces to create a balance between warmth, clarity, and modern structure. The primary heading typeface is Geist Sans, chosen for its clean geometric shapes and excellent legibility. Geist helps give the platform a contemporary feel while keeping titles, navigation, and UI labels sharp and easy to scan.

For body text, Lora is used as a complementary serif typeface. Lora adds a human, literary quality to the interface, making longer passages of text—such as form descriptions, notes, and informational content—more comfortable to read. This serif–sans pairing creates clear visual hierarchy without introducing distraction or visual noise.

Geist is reserved for headings, buttons, and key UI elements where clarity and quick recognition are essential. Lora appears in paragraphs, captions, and instructional text where warmth and readability matter most. Together, these two typefaces maintain a professional, approachable aesthetic that aligns with StudyStar’s focus on mindful study and personal progress.

[Back to top ⇧](#studystar)

## Features

### General

* Designed using a mobile-first approach to ensure usability on all device sizes.
* Fully responsive layout, with components adapting cleanly to tablets, laptops, and large screens.
* Hovering over buttons, links, or interactive areas changes the cursor to a pointer, reinforcing clickability.
* The base template includes the global navbar, sidebar menu, messages container, and footer for consistent UI across all pages.
* Uniform styling and layout choices ensure a seamless, cohesive experience across the entire platform.
* Success and error messages appear in a dedicated message area near the top of each page.
* These alerts provide immediate feedback when users submit forms, log sessions, update goals, or encounter errors.
* Messages are styled using Bootstrap alert classes for clear visual distinction.
* Multiple messages can appear at once, each in its own alert block.
* This unified approach improves usability, keeps users informed, and reduces confusion during interactions.

**Navigation bar**

* Always visible, offering quick access to important functionality such as the dashboard and user account options.
* Clean and minimal design ensures it never distracts from study content.
* Contains the StudyStar logo and a hamburger menu on mobile devices.

<img alt="Navbar" src="/readme-files/navbar_mobile.png" style="width:300px;">

**Sidebar Menu**

* Displays all main navigation links: Dashboard, Courses, Goals, Log Sessions, My Sessions, Achievements, and Logout.
* Always visible on screens wider than 767px.
* On mobile, it centers and remains at the top of the page.
* Menu items adapt based on authentication—only logged-in users see study tools.

<img alt="Sidebar Menu" src="/readme-files/sidebar.png" style="width:250px;">

**Footer**

* Visible on all pages with consistent styling matching the site theme.
* Contains copyright details, optional links (e.g., contact), and minimal branded styling.
* Provides a clean end-of-page anchor without overwhelming the layout.

<img alt="Footer" src="/readme-files/footer.png" style="width:350px;">

### Home Page

* Welcomes new users with a clear introduction to what StudyStar is and how it works.
* Includes quick links to log in, create an account, or navigate to the dashboard (if already logged in).
* Clean, motivational design encourages users to begin tracking their study journey.
* Highlights StudyStar’s core features: courses, goals, sessions, progress charts, and achievements.
* Displays an example of the User Interface with mockup accross devices.
* Provides an accessible, mobile-friendly layout.

<img alt="Home Page" src="/readme-files/home.png" style="width:600px;">

### Dashboard

Central hub for the StudyStar experience.

* Displays an overview of courses, achievements, recent activity, and quick actions.
* Provides motivational elements such as streak tracking, hours completed, and badges earned.
* Includes shortcuts to log a new session, add a course, or set a goal.

<img alt="Dashboard" src="/readme-files/dashboard.png" style="width:600px;">

###Courses

* Allows users to view, edit, and manage all their courses.
* Includes an “Add Course” button leading to a clean, well-structured form.
* Each course card shows status and colour.
* Clicking a course opens the course detail page.

<img alt="Courses" src="/readme-files/courses.png" style="width:600px;">

**Course Detail Page**

* Displays core information about the selected course: title, provider, status, description, dates, and assigned colour.
* Includes an “Add goal for this course” button for quick access to the add goal form.
* Designed for fast navigation between course content and study actions.

<img alt="Course Detail" src="/readme-files/course_detail.png" style="width:600px;">

**Add/Edit Course Form**

* The Add/Edit Course form provides a clean and intuitive interface for editing/creating a new course within StudyStar.
* Users can enter essential details such as the course title, provider, description, start and end dates, colour, and status.
* The form is designed using a simple vertical layout, ensuring readability and ease of use across all screen sizes.
* A colour picker or swatch-style selector allows users to assign a visual identifier to each course, helping distinguish them throughout the app.
* HTML5 date inputs provide a built-in date picker on compatible browsers for selecting course timelines.
* Validation messages appear inline, providing immediate feedback if required fields are missing or input is invalid.
* After submission, the user receives a success message and is redirected to the Courses page or the newly created course detail page, depending on your setup.
* The form maintains consistent styling with the rest of the platform, using StudyStar's colour palette, button styles, and spacing system.
* Fully responsive design ensures the form is easy to use on mobile devices, especially for users adding courses on the go.

<img alt="Course Form" src="/readme-files/course_form.png" style="width:600px;">

### Goals

* Users can view all goals, set new targets, and track weekly and long-term progress.
* Includes weekly hours, lessons, milestones, and other measurable metrics.
* Users can click the "+ Add New Goal" button taking the user to a dedicated, form-driven workflow.

<img alt="Goals" src="/readme-files/goals.png" style="width:600px;">

**Goal Detail Page**
* The Goal Detail page provides a clear, structured overview of a single study goal, allowing users to understand their progress at a glance.
* The Goal Details panel displays all key attributes, including the associated course, weekly targets, study days per week, calculated daily targets, milestone name and due date, and the total number of required lessons.
* A Progress Overview section highlights the user’s current performance. This includes the total hours completed for the current week (e.g., 2.0 / 2.0 hrs), overall goal completion percentage, and milestone progress.
* Motivational badges and messages appear when significant milestones are reached. For example:
“Weekly goal complete! Great job keeping pace.”
“Milestone achieved! You’ve completed your overall goal!”
* A Projected Finish Date is displayed when enough data is available to estimate the user’s completion timeline.
* The page features a Weekly Trend chart, allowing users to visualise their progress over time and identify study patterns or gaps.
* A detailed History Table lists all past weekly outcomes, including hours completed, lessons completed, and whether the weekly target was met.
* Action buttons at the bottom provide quick navigation options to Edit Goal, Delete Goal, or Return to Goals, helping users manage their study plans with ease.
* The layout is fully responsive and designed to match the broader StudyStar interface for a seamless user experience.

<img alt="Goal Detail" src="/readme-files/goal_detail1.png" style="width:600px;">
<img alt="Goal Detail" src="/readme-files/goal_detail2.png" style="width:600px;">

**Add/Edit Goal Form**

* The Add/Edit Goal form enables users to create/edit a personalised study goal linked to one of their existing courses.
* Users can enter weekly hour targets, weekly lesson targets, total required lessons, study days per week, and an optional milestone name and date.
* The form supports flexible goal types—users can create time-based, lesson-based, or hybrid goals depending on their learning style.
* A dropdown menu allows users to choose the associated course, ensuring goals are always linked correctly within the database.
* Inline validation ensures that required fields are completed and that values fall within acceptable ranges (e.g., study days between 1–7).
* The layout is clean and well-spaced, making the form approachable and easy to complete even on smaller screens.
* Submitting the form creates a new goal and redirects the user back to their Goals page or directly to the Goal Detail page where they can view progress immediately.
* A clear call-to-action button (“Create Goal”) is styled consistently with the rest of the StudyStar interface, using the primary colour scheme.
* Success and error messages appear at the top of the page, providing instant feedback on the form submission.

<img alt="Goal Form" src="/readme-files/goal_form.png" style="width:600px;">

### Achievements

* Displays all earned StudyStar achievements using your space-themed badge system.
* Highlights progress milestones such as hours completed, streaks, and goal completions.
* Motivates users and adds a fun, rewarding element to learning.
* Badges are displayed with titles and descriptions.

<img alt="Achievements" src="/readme-files/achievements.png" style="width:600px;">

### My Sessions

* The Study Session List page provides users with a clear, organised overview of all study sessions they have logged.
* Sessions are displayed in a clean, tabular layout, making it easy to scan key details such as date, duration, associated course, and optional notes.
* Each row includes essential metadata like the session start time and total minutes studied, helping users identify patterns in their study habits.
* Sessions are automatically ordered by most recent first, ensuring the latest activity is always the easiest to access.
* The table is fully responsive and adapts gracefully on mobile screens, stacking or compressing content as needed to maintain readability.
* Users can click on any session entry to view more detail or navigate to the associated course or goal, depending on the context.
* A dedicated “Log New Session” button at the top of the page makes it quick to add additional sessions without returning to the dashboard or course detail page.
* Pagination is included for users with a large number of sessions, preventing overwhelming the interface while keeping navigation simple.
* If no study sessions have been logged yet, a friendly placeholder message encourages users to log their first one, with a direct link to the session form.
* Consistent styling—using colour coding, spacing, and typography aligned with the StudyStar design system—ensures readability and a professional feel across devices.

<img alt="My Sessions" src="/readme-files/my_sessions.png" style="width:600px;">

**Log Study Session**

* Lets users record session details including duration, notes, and associated course or goal.
* Designed for quick entry, especially on mobile.
* Supports optional notes for reflection or revision tracking.
* Successful submissions trigger confirmation messages and update dashboard stats.

<img alt="Log Session Form" src="/readme-files/log_session.png" style="width:600px;">

**Delete Session/Goal/Course Confirm Page**

* The Delete Confirmation page provides a clear, focused prompt to ensure users do not accidentally remove important study data.
* When a user initiates a delete action—whether for a course, goal, or study session—they are taken to a dedicated confirmation screen that displays the name or title of the item being deleted.
* A concise message explains that the action is permanent, helping users understand the impact before proceeding.
* The page features two clear buttons:
    * A primary delete button, styled in a warning colour to draw attention and reinforce the seriousness of the action.
    * A cancel button, allowing users to return safely to the previous page without making changes.
* The layout is intentionally minimal to keep the user’s focus on the decision at hand without distractions.
* The confirmation interface follows consistent spacing, typography, and colour styles found throughout StudyStar.
* After deletion, users are redirected to the appropriate list view (e.g., Courses, Goals, Study Sessions) and shown a success message confirming the action.
* This approach ensures users have a clear, deliberate step before removing any item, reducing the risk of accidental data loss while still allowing them to manage their study records with confidence.

<img alt="Delete Confirm" src="/readme-files/delete_confirm.png" style="width:600px;">

### Contact Page

* Allows users to send queries, suggestions, or feedback directly from the website.
* Simple, clean Crispy Form with name, email, and message fields.
* Displays helpful success feedback after submission.
* Matches the overall StudyStar aesthetic for consistency.

<img alt="Contact Page" src="/readme-files/contact.png" style="width:300px;">

### Authentication Features (Sign Up, Sign In, Sign Out)**

**Create Account**

* Clear sign-up form asking for name, email, and password.
* Provides helpful validation messages for missing or invalid data.
* After signing up, users receive confirmation that their account is ready.
* Clean, readable layout consistent with the rest of the site.

<img alt="Sign Up" src="/readme-files/signup.png" style="width:300px;">

**Login**

* Accessible login form styled with Crispy Forms.
* Provides validation messages on incorrect credentials.
* Redirects to the dashboard upon successful login.

<img alt="Log In" src="/readme-files/login.png" style="width:300px;">

**Log Out**

* Shows a confirmation prompt before logging the user out.
* Uses Django’s secure logout flow.
* Displays a confirmation message upon successful logout.

<img alt="Log Out" src="/readme-files/logout.png" style="width:300px;">

## Technologies Used

### Languages Used

* [HTML5](https://en.wikipedia.org/wiki/HTML) Used for semantic page structure across all templates.
* [CSS3](https://en.wikipedia.org/wiki/CSS) Custom styling for layout, spacing, colour palette, and responsive design.
* [JavaScript](https://en.wikipedia.org/wiki/JavaScript) Adds interactivity, handles chart rendering, and enhances user experience on certain dynamic components.
* [Python](https://en.wikipedia.org/wiki/Python_(programming_language)) Core backend language used to power the Django framework, handle form processing, and manage business logic.
* [SQL](https://en.wikipedia.org/wiki/SQL) – Underlying language used by PostgreSQL for relational data storage and queries.

### Libraries and Frameworks

* [Django](https://www.djangoproject.com/)  – Provides the backend architecture, templating engine, ORM, form handling, authentication, and URL routing.

* [Bootstrap 5](https://getbootstrap.com/docs/5.3/getting-started/introduction/) – Front-end framework used for responsive layout, grid system, utility classes, and accessible UI components.

* [Chart.js](https://www.chartjs.org/) – Used for rendering interactive progress charts, weekly trends, and visual analytics.

* [Font Awesome](https://fontawesome.com/)– Icon library used for visual cues, buttons, and status indicators.

* [Google Fonts](https://fonts.google.com) (Geist & Lora) – Custom typography for headings and body text to create a clean, modern aesthetic.

### Django Packages and Dependencies

* [Django Crispy Form](https://django-crispy-forms.readthedocs.io/en/latest/) – Enhances form rendering and provides consistent, Bootstrap-aligned form styling.
* [Crispy Bootstrap 5](https://pypi.org/project/crispy-bootstrap5/) – Bootstrap 5 integration for Crispy Forms.
* [Django Allauth](https://django-allauth.readthedocs.io/en/latest/) – Manages user authentication, registration, login, logout, and password reset flows.
* [Gunicorn](https://gunicorn.org/) – Production-grade WSGI server used for deployment on Heroku.
* [Psycopg](https://www.psycopg.org/docs/) – PostgreSQL database adapter, enabling Django to communicate with the PostgreSQL backend.
* [DJ_Databse-URL](https://pypi.org/project/dj-database-url/) – Allows environment-based database configuration for production environments like Heroku.
* [WhiteNoise](https://whitenoise.readthedocs.io/en/stable/django.html) – Serves static files efficiently in production.

### Database Management

* [PostgreSQL](https://www.postgresql.org/) – Primary relational database used for all models, including Courses, Goals, Study Sessions, Goal Outcomes, and Contact Messages.
    * Managed through Django’s ORM, which handles migrations, schema updates, and safe relational querying.
    * Ensures data integrity through foreign keys, model constraints, and structured relationships.
    * Supports advanced querying and aggregation needed for generating progress statistics and achievement logic.

### Tools and Programs

* [Visual Studio Code](https://code.visualstudio.com/) – Version control used for tracking changes and managing feature updates.

* [GitHub](https://github.com) – Repository hosting, project tracking, and collaboration platform.

* [GitHub Issues/Projects](https://github.com/features/issues)  – Used for bug tracking, planning, and milestone documentation.

* [Heroku](https://www.heroku.com) – Cloud platform used for deploying the application, running the Django backend, and hosting the PostgreSQL database.

* Mermaid – Tools used to design ER diagrams, sitemaps, and architecture diagrams for documentation.

* [Chrome DevTools](https://developer.chrome.com/docs/devtools/) – Used for debugging layout, responsiveness, and front-end behaviour.

* [Balsamiq](https://balsamiq.com/) – Used during wireframing and early UI planning (include this if relevant).

* [Coolors](https://coolors.co) was used to create the colour palette image.

* [Am I Responsive](ami.responsivedesign.is) was used to preview the website across a variety of popular devices.

* [W3C Markup Validator](https://validator.w3.org/)
    - W3C Markup Validator was used to validate the HTML code.

* [W3C CSS Validator](https://jigsaw.w3.org/css-validator/)
    - W3C CSS Validator was used to validate the CSS code.

* [JSLint](https://jslint.com/) JavaScript Code Quality Tool was used to validate the JavaScript code.    

* [Favicon.io](https://www.favicon.io/) was used to create the site favicons.

[Back to top ⇧](#studystar)

## Testing

Extensive testing documentation can be found [here](/TESTING.md).

## Deployment

This website was developed using [Visual Studio Code](https://code.visualstudio.com/), which was then committed and pushed to GitHub using the terminal.

### Deploying on Heroku

The StudyStar project is deployed on Heroku using a PostgreSQL database and Django’s production settings. The following steps outline how to prepare the project and deploy it, either via GitHub integration (recommended) or via Git push from your local machine.

1. Prerequisites

    Before deploying, ensure you have:

    * A Heroku account
    * Git installed
    * A GitHub repository containing your project (all changes committed and pushed)
    * The Heroku CLI installed and logged in (heroku login) if you plan to use the CLI

2. Prepare the Project for Production

    * Install deployment dependencies (if not already installed):
    pip install gunicorn psycopg2-binary dj-database-url whitenoise
    *(Also include anything else you use, such as python-decouple.)

    * Freeze the requirements:
        pip freeze > requirements.txt


    * Create a Procfile in the project root (same level as manage.py):
        web: gunicorn studystar.wsgi

    * Replace studystar with your Django project name if different.

    * Configure static files in settings.py:

        STATIC_URL = "/static/"
        STATIC_ROOT = BASE_DIR / "staticfiles"
        STATICFILES_DIRS = [BASE_DIR / "static"]

        MIDDLEWARE = [
            "django.middleware.security.SecurityMiddleware",
            "whitenoise.middleware.WhiteNoiseMiddleware",
            # ...
        ]

        STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


    * Configure the database with dj-database-url (simplified example):

        import dj_database_url
        import os

        DATABASES = {
            "default": dj_database_url.parse(
            os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3"),
            conn_max_age=600,
            )
        }

    * In production, Heroku will provide DATABASE_URL automatically.

    * Set ALLOWED_HOSTS to include your Heroku app domain:

        ALLOWED_HOSTS = ["localhost", "127.0.0.1", "your-app-name.herokuapp.com"]

3. Create the Heroku App and Add PostgreSQL

    * You can do this via the Heroku Dashboard or CLI.

    * Via Dashboard:

        * Go to the Heroku Dashboard and click New → Create new app.
        * Choose a unique app name (e.g. studystar-app) and region, then create the app.
        * In the Resources tab, search for Heroku Postgres and add the Hobby Dev (Free) plan.

    * Via CLI:

        heroku create your-app-name
        heroku addons:create heroku-postgresql:hobby-dev --app your-app-name


    * Heroku automatically sets the DATABASE_URL config var for your app.

4. Configure Environment Variables (Config Vars)

    * In the Heroku Dashboard, go to Settings → Reveal Config Vars and add:

        SECRET_KEY – your Django secret key

        DEBUG – False

        Any other environment variables you rely on (email settings, etc.)

    * Optionally set via CLI:

        heroku config:set SECRET_KEY="your-secret-key" DEBUG="False" --app your-app-name

5. Deploying via GitHub (Recommended)

    * In the Heroku Dashboard, open your app and go to the Deploy tab.

    * Under Deployment method, select GitHub.

    * Click Connect to GitHub and authorise Heroku if needed.

    * Search for your repository (e.g. studystar) and click Connect.

    * Under Manual deploy, choose the branch you want to deploy (usually main) and click Deploy Branch.

    * Heroku will build the app using your requirements.txt, Procfile, and settings.

    * Once the build completes, you will see a “Your app was successfully deployed” message, and a View button to open the site.

    * You can optionally enable Automatic deploys so that every push to the selected branch triggers a new deployment.

6. (Optional) Deploying via Git (CLI)

    * If you prefer using the CLI instead of GitHub integration:

        * Ensure your code is committed locally:

            git add .
            git commit -m "Prepare for Heroku deployment"

    * Push the code to Heroku:

            git push heroku main

7. Run Migrations and Collect Static Files

    * After the first deployment, run these commands (either from the Heroku CLI or the More → Run Console option in the dashboard):

            heroku run python manage.py migrate --app your-app-name
            heroku run python manage.py collectstatic --noinput --app your-app-name

    * If you want to create a superuser:

        heroku run python manage.py createsuperuser --app your-app-name

8. Open the Deployed App

    Finally, open your live site:

        * From the Heroku Dashboard, click Open app, or

        * Use the CLI:

            heroku open --app your-app-name

The app should now be live, connected to a PostgreSQL database, and ready for users to create courses, goals, study sessions, and achievements.

### Forking the Repository

Forking a GitHub repository creates a personal copy of the original project on your own GitHub account. This allows you to explore the code, make changes, and experiment freely without affecting the original StudyStar repository.

**To fork this repository:**

    1. Log in to GitHub or create an account
    2. Navigate to the StudyStar GitHub Repository:
        https://github.com/TereBts/py_study_tracker
    3. At the top-right of the repository page, click “Fork”.
    4. GitHub will create a copy of the repository under your account, which you can now modify independently.

### Creating a Clone

Cloning allows you to create a local copy of the StudyStar repository so you can run the project in an IDE such as VS Code, PyCharm, or GitPod.

**To clone the repository:**

    1. Log in to GitHub
    2. Navigate to the StudyStar GitHub Repository.
    3. Click the green “Code” button.
    4. Under the HTTPS tab, copy the repository URL.
    5. Open your local IDE or terminal window.
    6. Navigate to the folder where you want the project to be stored.
    7. Run the following command, replacing the URL with the one you copied:
        git clone https://github.com/TereBts/py_study_tracker.git
    8. Press Enter. Git will download the repository and create a full local copy for you to work with.

For more information on cloning repositories, refer to GitHub’s documentation:
https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository

### User Authentication with Django Allauth
For user management and authentication, I implemented Django Allauth.This library provides a robust and secure foundation for handling account registration, login, logout, and password management without needing to build these features from scratch.

I chose Allauth because it:
* Integrates seamlessly with Django’s existing authentication system.
* Provides ready-to-use views and templates for signup, login, logout, and password reset.
* Supports email-based authentication, which suits StudyStar’s clean and professional user experience.
* Allows future scalability for adding social authentication (Google, GitHub, etc.) with minimal configuration changes.

**Setup Process**
    1. Installed and configured django-allauth and added it to INSTALLED_APPS.
    . Added allauth.account.middleware.AccountMiddleware and updated the AUTHENTICATION_BACKENDS.

    3. Defined key settings for authentication flow, including LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL, and SITE_ID.
    
    4. Updated the TEMPLATES configuration to include 'django.template.context_processors.request'.
    
    5. Added Allauth’s URL patterns under /accounts/ in the main urls.py.
    
    6. Configured the Sites framework in Django admin for both local and deployed environments.
    
    7. Created a @login_required tracker view and set up conditional navigation to display login/logout links dynamically.

### Installing and Using Bootstrap in the Project
Bootstrap was integrated into the StudyStar project to provide a responsive grid system, consistent design components, and accessible form styling with minimal custom CSS.

Why Bootstrap Was Used
Bootstrap offers a fast, reliable way to create a professional, mobile-friendly interface that adapts seamlessly to different screen sizes.It also integrates easily with Django templates and Allauth’s authentication views, allowing for cohesive UI design without heavy frontend frameworks.

**Bootstrap Integration Process**
    1. Add Bootstrap via CDNThe Bootstrap 5 library was linked in the base.html template to ensure that all pages extending it have access to the framework.

        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    2. At the bottom of the same template, the Bootstrap JavaScript bundle was included:
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    
    This provides Bootstrap’s JavaScript-powered components such as modals, dropdowns, and navigation toggles.
    
    3. Extend the Base Template:
    
        All pages (including the Allauth templates for login and signup) extend base.html so they automatically use Bootstrap styling and layout.
    
    4. Use Bootstrap Utility ClassesBootstrap’s grid system and utility classes (container, row, col-md-6, btn, card, etc.) were applied to structure the pages and forms.
    
    5. Customise with StudyStar ThemeA main.css file was added to the /static/css/ directory to override Bootstrap’s default colours and fonts with StudyStar’s palette and typography (Geist and Lora).
    
    6. Verify IntegrationThe login and signup templates were tested locally and on Heroku to ensure Bootstrap styles loaded correctly and the pages remained responsive.

**Local Setup**

Bootstrap is loaded via CDN, so no installation through npm or pip is required.However, to customise Bootstrap with your own colours and fonts, ensure the following setup is in place:

    * STATIC_URL and STATICFILES_DIRS are configured in settings.py.

    * Your custom stylesheet is linked after the Bootstrap CDN link so it overrides the defaults:<link rel="stylesheet" href="{% static 'css/main.css' %}">

Once these are in place, Bootstrap’s components and your StudyStar theme will work seamlessly together.

## Finished Product

| Page | Desktop | Mobile |
| --- | --- | --- |
| Home | ![Home desktop](readme-files/fp-home.png) | ![Home mobile](readme-files/fp-home-mobile1.png)![Home mobile2](readme-files/fp-home-mobile2.png) |
| About | ![About desktop 1](readme-files/fp-about1.png)![About desktop 2](readme-files/fp-about2.png) | ![About Mobile 1](readme-files/fp-about-mob1.png)![About Mobile 2](readme-files/fp-about-mob2.png)![About Mobile 3](readme-files/fp-about-mob3.png)![About Mobile 4](readme-files/fp-about-mob4.png) |
| Contact | ![Contact desktop](readme-files/fp-contact.png)  | ![Contact Mobile 1](readme-files/fp-contact-mob1.png)![Contact Mobile 2](readme-files/fp-contact-mob2.png) |
| Sign Up | ![Sign Up desktop](readme-files/fp-signup.png)  | ![Sign Up mobile](readme-files/fp-signup-mob.png) |
| Login | ![Login desktop](readme-files/fp-login.png) | ![Login mobile](readme-files/fp-login-mob.png) |
| Dashboard | ![Dashboard desktop](readme-files/fp-dashboard.png) | ![Dashboard Mobile1](readme-files/fp-dashboard-mob1.png)![Dashboard Mobile2](readme-files/fp-dashboard-mob2.png)![Dashboard Mobile3](readme-files/fp-dashboard-mob3.png)![Dashboard Mobile4](readme-files/fp-dashboard-mob4.png) |
| Courses | ![Courses desktop](readme-files/courses.png) | ![Courses Mobile](readme-files/fp-courses-mob.png) |
| Goals | ![Goals desktop](readme-files/fp-goals.png) | ![Goals mobile1](readme-files/fp-goals-mob1.png)![Goals mobile2](readme-files/fp-goals-mob2.png) |
| My Sessions | ![My Sessions desktop](readme-files/fp-sessions.png)| ![My Sessions mobile](readme-files/fp-sessions-mob1.png)![My Sessions mobile2](readme-files/fp-sessions-mob2.png) |
| Log Session | ![Log Session desktop](readme-files/fp-log-session.png) | ![Log Session mobile1](readme-files/fp-log-session-mob1.png)![Log Session mobile2](readme-files/fp-log-session-mob2.png) |
| Add Course | ![Add Course Form desktop](readme-files/fp-course-form1.png)![Add Course Form desktop 2](readme-files/fp-course-form2.png)| ![Add Course Form Mobile 1](readme-files/fp-course-form-mob1.png)![Add Course Form Mobile 2](readme-files/fp-course-form-mob2.png)![Add Course Form Mobile 3](readme-files/fp-course-form-mob3.png) |
| Add Goal | ![Add goal Form desktop](readme-files/fp-goal-form.png) | ![Add goal Form mobile 1](readme-files/fp-goal-form-mob1.png)![Add goal Form mobile 2](readme-files/fp-goal-form-mob2.png) |
| Logout| ![Logout desktop](readme-files/fp-logout.png) | ![Logout Mobile1](readme-files/fp-logout-mob1.png)![Logout Mobile2](readme-files/fp-logout-mob2.png) |
| Confirm Delete | ![Confirm Delete Desktop](readme-files/fp-confirm-delete.png) | ![Confirm Delete Mobile](readme-files/fp-confirm-delete-mob.png) |
| Error 404 | ![Error 404 desktop](readme-files/fp-404.png) | ![Error 404 mobile 1](readme-files/fp-404-mob1.png)![Error 404 mobile 2](readme-files/fp-404-mob2.png) |

[Back to top ⇧](#studystar)

## Reflections

**Model Design, User Experience, and Early Decisions**

When I first created the Course model and tested the form in the Django Admin, I realised that allowing users to manually enter their own slug felt far too technical and unnecessary for the StudyStar audience. I removed the field from the form and ensured that all slugs would be created automatically on save.
I also changed direction with course colours: originally users selected a hex code, but this again felt too specialist. I replaced it with a friendly colour-select dropdown using pre-defined choices. These early adjustments helped shape StudyStar’s identity as a simple, accessible productivity tool rather than a technical interface.

**Confetti Celebration Attempt**

I attempted to add a JavaScript confetti celebration effect whenever a goal was completed. I tested this on both the Goal List and Goal Detail pages, but the animation refused to trigger consistently. Because it wasn’t a core requirement, I made the decision to postpone it and focus on core functionality first. This became a recurring theme in the project: prioritising reliability and clear UX over extras unless time allowed.

**Building and Testing the Goal Record Freeze Feature**

Developing the Goal Record Freeze feature was a key milestone for ensuring data integrity and predictable weekly tracking. I combined automated unit tests (to validate backend logic) with manual UI testing to verify the feature in a real user workflow.

Writing the automated test first helped isolate logic errors early, then manually testing the full Django flow (models → views → templates) confirmed that real users would experience freeze logic exactly as expected.

This highlighted the importance of verifying not only code correctness, but the behavioural outcomes seen by the user.
Going forward, I plan to extend this practice by:
* Adding feature/integration tests for Achievements and Analytics,
* Introducing scheduled automation for weekly freeze tasks (Heroku Scheduler or Celery Beat),
* Ensuring every major feature has both automated tests and UI-level validation before release.

Together, these practices help maintain user trust in the accuracy of their study data.

**Filtering User-Specific Data in Forms**

When building the Study Session logging form, I discovered that dropdowns were showing every Course and Goal in the database, not just the user’s own. The problem came from Django ModelForms automatically populating foreign-key fields with all objects unless explicitly filtered.

This caused an interesting bug: my Course model uses an owner field while Goal uses user. Because my form filtered by user for both, Django raised a FieldError for Courses (“Cannot resolve keyword 'user' into field”).

I resolved it by:

* Passing the current user into the form via get_form_kwargs(), and

* Filtering each queryset separately:

    self.fields["course"].queryset = Course.objects.filter(owner=user)
    self.fields["goal"].queryset = Goal.objects.filter(user=user, is_active=True)

This ensured privacy and a clearer UX.

This issue taught me how Django forms pull querysets, how to pass custom context into forms, and how small naming inconsistencies (user vs owner) can cause permission and logic errors. After applying the fix, the form became intuitive and fully user-specific.

**Visualising Goal History**

Building the Goal History chart was one of the most rewarding visual features. It turned raw weekly data into an engaging, motivating progress graph.

Initially, the chart didn’t render at all — a blank canvas. This helped me learn how Django outputs Python lists differently from JSON, and I fixed the problem by using the json_script tag. This reinforced secure, reliable ways of transferring Python data to JavaScript.

To make the feature demonstrable, I also wrote a custom management command to seed test GoalOutcome entries. This strengthened my understanding of Django’s ORM, custom commands, and end-to-end feature testing.

In the context of StudyStar, this visual feedback helps users reflect on habits and stay motivated, which aligns with the app’s core purpose.

**Developing the Achievements System**

The Achievements system started as a simple “reward users” idea, but evolved into a modular, scalable, rule-based engine. I created two models:

* Achievement (badge definitions & rules)

* UserAchievement (awarded badges)

I originally considered Django signals but instead opted for an evaluator service (evaluate_achievements_for_user) to keep logic explicit, testable, and extendable. This was the right decision — it kept the system maintainable and allowed me to safely add new rules later.

The Achievements page, dashboard summary, and recent badge unlocks also required refining rule logic, fixing some incorrect field references, and ensuring each badge could only be awarded once. This feature demonstrates full-stack integration: models, services, views, templates, and UI messaging all working together.

**Dashboard Evolution and Design Direction**

The dashboard went through several redesigns before becoming a unified hub for the StudyStar experience.

Originally it displayed simple stats and recent outcomes, but I redesigned it to:

* Replace “recent outcomes” with a meaningful monthly trend chart,

* Move Achievements into a top-level summary to make the experience more motivational,

* Make the chart full-width for clarity,

* Improve the layout for responsiveness and readability,

* Add a sidebar navigation for logged-in users.

This decision clearly separated the authenticated user experience from the public home page and helped create a cohesive, calm, productivity-focused UI. The evolution of the dashboard taught me that good UX is iterative: each round of testing and design refinement pushed the interface closer to what users actually need.

**Additional Reflections on Changing Direction, Debugging, and Project Growth**

**Refactoring the Data Models Mid-Build**

As StudyStar grew, I found myself revisiting my models multiple times — for example, adjusting relationships between Goal, StudySession, and GoalOutcome, and moving logic out of models and into service functions. Early on, I tried placing too much logic directly in model methods, but later refactored this into clearer service layers, improving testability and separation of concerns.

**Naming Conventions and Consistency Lessons**

The user vs owner inconsistency taught me how easily small naming decisions can create bugs later. This experience convinced me to maintain consistent naming conventions throughout future models.

Template Structure and Reusability

As the project expanded, I reorganised templates into logical app folders with a clear naming structure. I also introduced reusable template partials to reduce duplication (e.g., forms, dashboard sections, icon blocks). This improved maintainability and reduced future debugging.

**CSS and Responsiveness Challenges**

I faced several unexpected layout issues — especially on smaller devices. Some Bootstrap behaviours didn’t work as expected, so I had to override padding, flexbox rules, and table behaviour to ensure mobile usability. These challenges improved my understanding of breakpoints and responsive utility classes.

**JavaScript Debugging**

Working with Chart.js brought several debugging sessions, mostly revolving around:

* Missing canvas contexts

* Data not rendering due to Python/JS formatting,

* Undeclared variables caught by online validators.

This taught me the value of linting, structured JSON data, and simplifying scripts into clear functions.

**Changing Direction with Features**

Throughout the project, I dropped or postponed several feature ideas (like confetti, sound notifications, and animated streak indicators) because they weren’t core to the MVP. This helped keep the project focused and prevented scope creep — a valuable lesson for real-world development.

**Balancing Functionality and Assessment Requirements**

Some decisions were influenced by the need to clearly demonstrate:

* CRUD operations
* Authentication flows
* Data visualisation
* Testing
* Model relationships

This helped shape the direction and prioritisation of features in StudyStar’s final version.

### Future Features

StudyStar has been designed with scalability in mind, and there are several features planned to enhance the platform’s usability, motivation tools, and social experience. Future development will focus on deeper analytics, improved user control, and intelligent support.

**Expanded Data Visualisation**

I plan to increase the amount of data visualisation across the platform, introducing new charts, graphs, and analytical summaries. This might include:

* Progress timelines for each Course,
* Streak visualisers
* Session heatmaps showing study patterns
* Comparison charts showing targets vs. actual performance.

These additions will help learners interpret their study habits more clearly and stay motivated through visual feedback.

**Editing and Managing Study Sessions**

Currently, users can log and delete study sessions, but a full edit feature will be added. This will allow users to:

* Edit duration, notes, and associated course/goal
* Correct mistakes
* Update sessions as their plans change

This will improve accuracy and reinforce user control over their data.

**User Profile Editing**

A simple user profile section will allow users to:

* Create a custom username
* Write a short bio
* Upload a profile image or avatar.

This feature will form the foundation for future social interactions in the app.

**Social Features and Following System** 

To make StudyStar a more connected space, I plan to introduce a way for users to “follow” friends or classmates. This will allow optional sharing of:

* Achievements
* Badges
* Weekly progress summaries
* A limited public profile

This will encourage accountability, gentle peer motivation, and community-building through positive reinforcement.

**Mobile-Friendly Sidebar Navigation**

The current sidebar works well on desktop, but a mobile-first version will be added. This will include:

* A collapsible panel
* A slide-in/slide-out animation,
* A hamburger menu trigger

This update will improve navigation for mobile users and make StudyStar feel more like a modern, app-like interface.

**AI-Powered Progress Analysis**

A planned integration with an AI API will allow StudyStar to provide personalised motivational messages and tailored study insights. Potential features include:

* Dynamic recommendations based on study patterns
* Encouragement based on streaks or milestones
* Gentle nudges during quieter weeks
* Reflective summaries of the user’s month.

This aligns with StudyStar’s goal of supporting users in both practical planning and emotional motivation.

**Additional Future Enhancements** 

Alongside the major features above, several other improvements are planned:

* Recurring or Scheduled Goals:
    Allow users to set goals that repeat weekly or monthly without manually resetting them.

* Time Estimates and Forecasting:
    Use past data to predict whether users are on track to meet deadlines.

* Improved Accessibility Support:
    Increase ARIA labelling, colour contrast controls, and keyboard navigation to ensure the platform is fully accessible.

* Course and Goal Sharing Templates:
    Auto-generate shareable cards (images or summaries) that users can post on social media or send to study partners.

* Export Tools (CSV / PDF):
    Give users the option to export their study history, outcomes, or achievements.

* Public API (Long-term):
    Potentially expose a limited API so users can connect StudyStar to third-party tools or integrate their data elsewhere.

* Automated Email Notifications, Summaries + Reminders
    Allow users to set up notification settings so they can receive summaries and reminders based on their progress in their email inbox. 

## Credits 

### Content

* All content was written by the developer.

### Media

* StudyStar logo: Created by the developer in ChatGPT's Logo Creator
* Home page mockup image: Sourced from [Freepik](https://www.freepik.com/) and edited by the developer in [Affinity Studio](https://www.affinity.studio/)
* About Page Illustration: Created by the developer in [Canva](https://www.canva.com/)
* Contact Page Illustration: Created by the developer in [Canva](https://www.canva.com/)
* Dashboard Monthly Study Trend Chart: Created by the developer with [ChartJS](https://www.chartjs.org/)
* Goal Detail Weekly Trend Chart: Created by the developer with [ChartJS](https://www.chartjs.org/)

