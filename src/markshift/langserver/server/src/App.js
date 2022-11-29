import logo from './logo.svg';
import './App.css';
import React from 'react';
import {createElement, Fragment, useEffect, useState} from 'react'
import {unified} from 'unified'
//import math from 'react-math'
import rehypeParse from 'rehype-parse'
import rehypeReact from 'rehype-react'
import rehypeKatex from 'rehype-katex'
import rehypeHighlight from 'rehype-highlight'

//import parse, {domToReact} from 'html-react-parser';
//const html = `<div>a text is written as html. </div><img width="50%" src="https://www.bing.com/th?id=OHR.RedPlanetDay_IT-IT1471017689_UHD.jpg" alt="image"/>`;

function App() {
  const [content, setContent] = useState('<div>Loading...</div>')
  //const [count, setCount] = useState(0);
  const [reactFragment, setReactFragment] = useState(React.Fragment)

  useEffect(() => {
    window.addEventListener('pywebviewready', function() {
      if (!window.pywebview.state) {
        window.pywebview.state = {}
      }
      // Expose setContent in order to call it from Python
      window.pywebview.state.setContent = setContent

      const event = new CustomEvent('pywebview_state_ready');
      window.dispatchEvent(event);
    })
  }, []);

  // useEffect(() => {
  //     const id = setInterval(() => {
  //         setCount(t => t + 1);
  //         setContent("<div>timer update <strong>: " + parseInt(count) + " +  rehype technology </strong></div><br>"+
  //             '<p>Lift(<span class="math math-inline"><span class="katex">O(n^{' + parseInt(count) + '})</span></span>) can be determined by Lift Coefficient (<span class="math math-inline"><span class="katex">O(n^2)</span></span>) like the following equation.</p><div class="math math-display"><span class="katex-display">a=b^{'+parseInt(count/2)+'}+c</span></div>'+
  //             '<iframe src="https://www.youtube.com/embed/2NGjNQVbydc" width="560" height="315" title="A YouTube video" frameborder="0" allowfullscreen></iframe>');
  //     }, 100);
  //     return () => clearInterval(id);
  // }, [count]);

  useEffect(() => {
    unified()
      .use(rehypeParse, {fragment: true})
      .use(rehypeKatex)
      .use(rehypeHighlight)
      .use(rehypeReact, {createElement, Fragment})
      .process(content)
      .then((file) => {
        setReactFragment(file.result)
      })
  }, [content])

  return (
    <div className="App">
      <body className="App-Body">
      {reactFragment}
      </body>
    </div>
  );
}

export default App;
