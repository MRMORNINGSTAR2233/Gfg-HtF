# RecruitAI - Multi-Agent Recruitment Platform

A modern recruitment application frontend built with Next.js, TailwindCSS, and ShadCN UI components. This project provides an intuitive interface for a multi-agent recruitment system.

## Features

- **Home Page**: Introduction to the platform with key features
- **Job Description Submission**: Submit and analyze job descriptions
- **Candidate Upload**: Upload CVs and match them with job descriptions
- **Dashboard/Analytics**: View candidate matches, statuses, and recruitment metrics

## Technologies Used

- **Next.js**: React framework for building the application
- **TailwindCSS**: Utility-first CSS framework for styling
- **ShadCN UI**: Component library for modern, accessible UI elements
- **React Hook Form**: For managing form state and validation

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend server running (see backend README)

### Installation

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Create a local environment file:
```bash
cp .env.local.example .env.local
```

3. Update the `.env.local` file with your backend URL:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
# or
yarn dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Using the Application

### Job Description Submission

1. Navigate to the "Job Description" page from the dashboard or directly at `/job-description`
2. Fill out the job details form with:
   - Job Title
   - Company Name
   - Location
   - Detailed job description
3. Click "Submit Job Description" to process the job
4. View AI-generated analysis results on the right side panel

### Candidate CV Upload

1. Navigate to the "Upload CV" page from the dashboard or directly at `/candidate-upload`
2. Fill out the candidate details:
   - Full Name
   - Email Address
   - Select a job description to match against
3. You can provide the resume content in two ways:
   - Paste the resume text directly into the text area
   - Click the "Upload File" button to select a file from your computer
     - Supported formats: `.txt`, `.pdf`, `.doc`, `.docx`
     - Text files (.txt) will be read and displayed in the text area
     - Other formats will be sent directly to the server for processing
4. Click "Submit Application" to process the CV
5. View match results and analysis on the right side panel

### Dashboard

The dashboard provides a real-time overview of your recruitment process:

1. View key metrics at the top:
   - Active Jobs
   - Candidates
   - Average Match Score
   - Scheduled Interviews
2. Use the tabs to switch between candidates and jobs views
3. Click the "Post New Job" button to create a new job description
4. Click the "Upload CV" button to submit a new candidate
5. View candidate and job details by clicking the "View" button in each row

## File Upload Support

The application supports various file formats for candidate resumes:

- **Text files (.txt)**: Contents are read directly and displayed in the text area
- **PDF files (.pdf)**: Sent to the backend for processing
- **Word documents (.doc, .docx)**: Sent to the backend for processing

## Customization

You can customize the application by modifying the following:

- Update the API URL in `.env.local` to point to your backend server
- Modify UI components in the `src/components` directory
- Update styles in the TailwindCSS configuration

## Backend Integration

This frontend application connects to a FastAPI backend that processes job descriptions and CVs using AI. Ensure the backend server is running and properly configured before using this application.

To connect to the backend:

1. Make sure the backend server is running (typically on port 8000)
2. Verify that your `.env.local` file has the correct `NEXT_PUBLIC_API_URL` value
3. The frontend will automatically connect to the backend API for all operations

## Troubleshooting

- **API Connection Issues**: Check that the backend server is running and the `NEXT_PUBLIC_API_URL` is correct in your `.env.local` file
- **File Upload Problems**: Ensure the file format is supported and the file size is reasonable (under 10MB)
- **Empty Dashboard**: Submit job descriptions and candidate CVs to populate the dashboard

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Project Structure

```
frontend/
├── src/                    # Source files
│   ├── app/                # Next.js App Router pages
│   │   ├── page.tsx        # Home page
│   │   ├── job-description/# Job description page
│   │   ├── candidate-upload/# Candidate upload page
│   │   └── dashboard/      # Dashboard page
│   ├── components/         # React components
│   │   ├── ui/             # UI components from ShadCN
│   │   └── navbar.tsx      # Navigation component
│   └── lib/                # Utility functions
├── public/                 # Static files
└── package.json            # Dependencies and scripts
```

## Learn More

To learn more about the technologies used:

- [Next.js Documentation](https://nextjs.org/docs)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [ShadCN UI Documentation](https://ui.shadcn.com)

## Deployment

The application can be deployed to Vercel or any other hosting service that supports Next.js applications.
