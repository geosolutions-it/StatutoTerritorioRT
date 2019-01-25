const axios = require('axios');
const fs = require('fs');
const argv = require('yargs').argv

if(!argv.token || !argv.session) {
    console.log("Missing parameters")
    console.log("updateFragmentsTypes.js --token OoKIwLIMLN34aK3gwtvcfR63nWwt144wPn7Pv4UcGkkoemmqOgOEBXZG0Agf5lhq --session wekus3r1kf2608t3o58xj8ipm2f6mj9f")
    process.exit(0)
}
const config = {
    url: 'http://127.0.0.1:8000/serapide/graphql',
    method: 'POST',
    data: JSON.stringify({
        variables: {},
        query: `
          {
            __schema {
              types {
                kind
                name
                possibleTypes {
                  name
                }
              }
            }
          }
        `
      }),
    headers: {
        'Host': '127.0.0.1:8000',
        'Accept': 'application/json',
        'X-CSRFToken': `${argv.token}`,
        'Content-Type': 'application/json',
        'Cookie': `csrftoken=${argv.token}; sessionid=${argv.session}`
        },
    validateStatus: () => true
  };

  axios.request(config).then(({status, data}) => {console.log(status); return data.data})
    .then(d => {
    // here we're filtering out any type information unrelated to unions or interfaces
    const filteredData = d.__schema.types.filter(
      type => type.possibleTypes !== null,
    );
    d.__schema.types = filteredData;
    fs.writeFile('./src/fragmentTypes.json', JSON.stringify(d), err => {
      if (err) {
        console.error('Error writing fragmentTypes file', err);
      } else {
        console.log('Fragment types successfully extracted!');
      }
    });
  })