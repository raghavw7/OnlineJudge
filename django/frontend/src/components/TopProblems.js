import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TopProblems = () => {

    const [prob, setProb] = useState(null);

    useEffect(() => {
            const fetchtopproblems = async () => {
                try {
                    const response = await axios.get('/top_problems/', {
                    headers: {
                    'Content-Type': 'application/json/'
                    }
                });
                setProb(response.data.top_problems)
                }
                catch {
                    console.log('Error getting the top problems')
                    setProb({error: 'Failed. Please retry.'})
                }
            };
            fetchtopproblems();
    }, []); // Empty dependency array means this effect runs once, when the component mounts



    return (
        <div>
            {prob ? (
                <div>
                    <h4>Top Problems:</h4>
                    <ul class="list-group">
                        {prob.map((prob, index) => (
                            <li class="list-group-item" key={index}>{prob.title}</li>
                        ))}
                    </ul>
                </div>
            ) : (
                <p>Loading...</p>
            )}
        </div>
    );

};

export default TopProblems;