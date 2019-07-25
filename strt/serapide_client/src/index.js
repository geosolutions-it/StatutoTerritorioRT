import React from 'react'
import ReactDOM from 'react-dom'
import './index.css'
import App from './App'
import OnlyNavBar from './OnlyNavBar';
const el = document.getElementById('only-nav-bar');
if (!el) {
  ReactDOM.render(<App />, document.getElementById('serapide'))
}else {
  ReactDOM.render(<OnlyNavBar />, el)
}
// needed to prevent page reload on code update
if (module.hot && process.env.NODE_ENV === 'development') {
  module.hot.accept()
}
