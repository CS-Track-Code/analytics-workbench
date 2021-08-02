const express = require('express') ;
const app = express() ;
const port = 8888  ;
//var counter = 0;
app.get('/myapp/', function (req, res) {
    const Mercury = require('@postlight/mercury-parser');
    const url = req.query.url;
    console.log('Request for: ' + url);
    Mercury.parse(url).then(result => {  res.send(result);  } );
    /*counter += 1;
    if (counter >= 14){
        console.log("STOPPING");
        process.exit(1);
    } else{
        console.log(counter + " done");
    }*/
});
app.listen(port);
