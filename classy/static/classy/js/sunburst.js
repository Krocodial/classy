var classification_mapping = JSON.parse(document.getElementById("classification_mapping").textContent);
var options = JSON.parse(document.getElementById("options").textContent);

console.log(classification_mapping);

for (i = 0; i < options.length; i++) {
    console.log(classification_mapping[options[i]]['orig']);
}


data = {

}
/*
const sunburst = Sunburst();
sunchart
    .data()
    ();
*/
