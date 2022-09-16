const express = require("express");
const request = require("request");
const fetch = (...args) =>
  import("node-fetch").then(({ default: fetch }) => fetch(...args));
const app = express();

const PORT = 3010;
const CONTENT_TYPE_JSON = {'Content-Type': 'application/json' }
const EMPTY_JSON = "{}"

app.get("/contents/:idUser", async (req,res) => {
  var idUser  = req.params.idUser
  console.log("Retrieve utility content for user "+ idUser)
  
  let utilityContent = {score: 5}
  res.set(CONTENT_TYPE_JSON)
  res.send(utilityContent)
})

app.get("/", (req, res) => {
  res.status(200).send("200 OK");
});

app.listen(process.env.PORT || PORT, () => {
  console.log("Escuchando en puerto =>", PORT);
});
