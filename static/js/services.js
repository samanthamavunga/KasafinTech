// get all modal buttons and modal dialogs
var modalButtons = document.querySelectorAll('.modal-button');
var modalDialogs = document.querySelectorAll('.modal');

// add click event listener to each modal button
modalButtons.forEach(function(modalButton, index) {
  // add click event listener to modal button
  modalButton.addEventListener('click', function() {
    // display the modal dialog
    modalDialogs[index].style.display = 'block';
  });

  // add click event listener to close button
  var closeButton = modalDialogs[index].querySelector('.close-button');
  closeButton.addEventListener('click', function() {
    // hide the modal dialog
    modalDialogs[index].style.display = 'none';
  });

  // add click event listener to modal content
  var modalContent = modalDialogs[index].querySelector('.modal-content');
  modalContent.addEventListener('click', function(event) {
    // if the user clicks outside of the modal content, hide the modal dialog
    if (event.target == modalDialogs[index]) {
      modalDialogs[index].style.display = 'none';
    }
  });
});
