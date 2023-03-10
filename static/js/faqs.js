var accordionItems = document.querySelectorAll(".accordion-item");

accordionItems.forEach(function(item) {
  var header = item.querySelector(".accordion-item-header");
  var body = item.querySelector(".accordion-item-body");

  header.addEventListener("click", function() {
    // Close all answer sections except for the clicked one
    accordionItems.forEach(function(otherItem) {
      if (otherItem !== item) {
        otherItem.classList.remove("active");
        otherItem.querySelector(".accordion-item-body").style.maxHeight = null;
      }
    });

    // Toggle the visibility of the clicked answer section
    item.classList.toggle("active");
    if (item.classList.contains("active")) {
      body.style.maxHeight = body.scrollHeight + "px";
    } else {
      body.style.maxHeight = null;
    }
  });
});
