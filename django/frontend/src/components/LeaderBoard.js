import React, { useState, useEffect } from 'react';
import axios from 'axios';

const LeaderBoard = () => {

    const [toppers, setToppers] = useState(null);

    useEffect(() => {
        const fetchToppers = async () => {
            try {
                const response = await axios.get('/leaderboard/', {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                setToppers(response.data.toppers);
            }
            catch (error) {
                console.error("Error retrieving data.");
                setToppers({ error: 'Failed. Please retry.' });
            }
        };

        fetchToppers();
    }, []); // Empty dependency array means this effect runs once, when the component mounts

    return (
        <div>
            {toppers ? (
                <div>
                    <h4>Top Performers:</h4>
                    <ul class="list-group">
                        {toppers.map((topper, index) => (
                            <li class="list-group-item" key={index}>{topper.username}</li>
                        ))}
                    </ul>
                </div>
            ) : (
                <p>Loading...</p>
            )}
        </div>
    );
};

export default LeaderBoard;
