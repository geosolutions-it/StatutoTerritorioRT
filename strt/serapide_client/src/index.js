import React from 'react'
import ReactDOM from 'react-dom'
import './index.css'
import App from './App'

ReactDOM.render(<App />, document.getElementById('serapide'))
// needed to prevent page reload on code update
if (module.hot && process.env.NODE_ENV === 'development') {
  module.hot.accept()
}
