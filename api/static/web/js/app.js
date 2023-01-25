const image_input = document.querySelector("#uploaded_img");
const form_detect = document.getElementById("form_detect")
var uploaded_image = ""
form_detect.style.visibility = 'hidden'

image_input.addEventListener("change", function() {
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    uploaded_image = reader.result;
    var imgtag = document.getElementById("my_preview");
    imgtag.src = uploaded_image;
    form_detect.style.visibility = 'visible'

  })
  reader.readAsDataURL(this.files[0]);
  // TODO: delete console.log
  console.log(this.files[0].name) 
  
})