import React, {useState} from 'react';
import axios from 'axios';
import {Editor} from '@monaco-editor/react';


const CodeSubmission = ({problemId}) => {
    const [code, setCode] = useState('');
    const [language, setLanguage] = useState('cpp');
    const [result, setResult] = useState(null);
    const [inputs, setInputs] = useState('');
    const [showInputs, setShowInputs] = useState(false);
//    const [accepted, SetAccepted] = useState(false)
//    const [resultshow, setResultShow] = useState(false)


    const handleEditorChange = (value) => {
        setCode(value);
    };

    const handleInputsChange = (e) => {
        setInputs(e.target.value)
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log('Submitting code : ', code, 'for problem : ', problemId, 'in language : ', language)
        const submissionData = {code, language, problemId};

        try {
            const response = await axios.post('/problems/run_solution_react/', submissionData, {
                headers: {
                    'content-Type': 'application/json',
                },
            });
            setResult(response.data);

        } catch (error) {
            console.error('Error submitting code:', error);
            setResult({error: 'Submission failed. Please retry.' });
        }
    };

    const handleCompile = async(e) => {
        e.preventDefault();
        setShowInputs(true)
        console.log('Compiling the code: ', code, ' with inputs: ', inputs, ' in language: ', language)
        const compilationData = {code, language, inputs};

        try {
            const response = await axios.post('/problems/run_solution_react/', compilationData, {
                headers: {
                    'content-Type':'application/json',
                },
            });
            setResult(response.data);
        }
        catch (error) {
            console.error('Error compiling the code', error);
            setResult({error: 'Compilation failed. Please retry.'})

        }
    };


    return (
    <div className="container">
    <form  onSubmit={handleSubmit} className="form-group">

    <div className="mb-3">
        <label htmlFor="language" className="form-label"> Select Language </label>
        <select
            id="language"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="form-select">

            <option value="cpp"> C++ </option>
            <option value="python"> Python </option>
            <option value="java"> Java </option>
        </select>
    </div>



    <div className="mb-3">
        <Editor
            height="370px"
            language={language === 'cpp'? 'cpp' : language}
            value = {code}
            onChange = {handleEditorChange}
            theme = "vs-dark"
            options={{
                selectOnLineNumbers: true,
                automaticLayout: true,
            }}
        />
    </div>

    {showInputs && (
        <div className="mb-3">
        <label htmlFor="inputs" className="form-label"> Inputs </label>
        <textarea
            id='inputs'
            value = {inputs}
            onChange = {handleInputsChange}
            className = "form-control"
            placeholder = "Enter inputs for compilation"
        />
        </div>
    )}


    <div>
        <button
            type="compile"
            className="btn btn-primary"
            onClick = {handleCompile}>
            Compile
        </button>
        <button
            type="submit"
            className="btn btn-primary"
            onClick = {handleSubmit}>
            Submit
        </button>
        <br />
    </div>

    </form>
    <br />
    {result && (result.result === 'passed' ? (
      <div className="alert alert-success d-flex align-items-center" role="alert">
        <svg
          className="bi flex-shrink-0 me-2"
          width="24"
          height="24"
          role="img"
          aria-label="Success:"
          viewBox="0 0 16 16"
          fill="currentColor"
        >
          <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
        </svg>
        <div>
          {result.result}
        </div>
      </div> ) :
      (
        <div className="alert alert-warning d-flex align-items-center" role="alert">
          <svg
            className="bi flex-shrink-0 me-2"
            width="24"
            height="24"
            role="img"
            aria-label="Warning:"
            viewBox="0 0 16 16"
            fill="currentColor"
          >
            <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
          </svg>
          <div>
            {result.result}
          </div>
        </div>
      ))

    }
</div>
);
};


export default CodeSubmission;