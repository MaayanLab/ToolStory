import React from "react";
import { BrowserRouter as Router, Link, Route } from "react-router-dom";
import Admin from './Admin';
import DBCK from './DBCK';
import Home from './Home';
import Query from './Query';
import Stats from './Stats';

const App = () => (
  <Router>
    <div>
      <ul>
        <li>
          <Link to="/signature-commons-ui/">Home</Link>
        </li>
        <li>
          <Link to="/signature-commons-ui/query">Query</Link>
        </li>
        <li>
          <Link to="/signature-commons-ui/stats">Stats</Link>
        </li>
        <li>
          <Link to="/signature-commons-ui/dbck">Database Check</Link>
        </li>
        <li>
          <Link to="/signature-commons-ui/admin">Admin</Link>
        </li>
      </ul>

      <Route exact path="/signature-commons-ui/" component={Home} />
      <Route exact path="/signature-commons-ui/query" component={Query} />
      <Route exact path="/signature-commons-ui/stats" component={Stats} />
      <Route exact path="/signature-commons-ui/dbck" component={DBCK} />
      <Route exact path="/signature-commons-ui/admin" component={Admin} />
    </div>
  </Router>
)

export default App;
