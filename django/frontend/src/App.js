import React from 'react';
import { createRoot } from 'react-dom/client';
import CodeSubmission from './components/CodeSubmission';
import LeaderBoard from './components/LeaderBoard';
import TopProblems from './components/TopProblems'
const problemId = window.problemId;

const codeSubmissionDiv = document.getElementById('code-submission-root');
if (codeSubmissionDiv) {
    createRoot(codeSubmissionDiv).render(<CodeSubmission problemId={problemId} />);
}

document.addEventListener('DOMContentLoaded', () => {
    const leaderboardDiv = document.getElementById('leaderboard');
    if (leaderboardDiv) {
        const root = createRoot(leaderboardDiv);
        root.render(<LeaderBoard />);
    }
})

document.addEventListener('DOMContentLoaded', () => {
    const topProblemDiv = document.getElementById('top_problems');
    if (topProblemDiv) {
        const root = createRoot(topProblemDiv);
        root.render(<TopProblems />);
    }
})
