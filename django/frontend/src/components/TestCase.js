import React, {useState, useEffect} from 'react';
import axios from 'axios'

const ShowTestcase = () => {

    const [tc, setTc] = useState(null);


    useEffect(()=> {
        const fetchTestCases = async () => {
        try {
            const response = await axios.get('/test_cases/9', {
                headers: {
                'Content-Type': 'application/json',
                }})

            setTc(response.data.testcases);
        }
        catch (error) {
            console.log("Failed to load testcases ", error);
            setTc(null);
        }
        }
        fetchTestCases();
    }, []);

return (
<>
    {tc? (<div>
        <h5>TestCases</h5>
        <ul class=''>
        {tc.map((testcase, index) => (
            <li class='list-group' key={index}> {testcase.input} -> {testcase.output} </li>))
        }
            </ul>
    </div>) : (<p> Loading...</p>)}
</>
)};

export default ShowTestcase;