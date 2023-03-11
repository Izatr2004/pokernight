
function openModal(tip, dealer) {
    var modal = document.getElementById("myModal");
    var span = modal.getElementsByClassName("close")[0];
    var content = document.getElementById("modalContent");
    var i = dealer;

    // Set the tip value in the hidden input field
    var inputTip = document.createElement("input");
    inputTip.setAttribute("type", "hidden");
    inputTip.setAttribute("name", "tip");
    inputTip.setAttribute("value", tip);

    // Set the dealers value in the hidden input field
    var inputDealers = document.createElement("input");
    inputDealers.setAttribute("type", "hidden");
    inputDealers.setAttribute("name", "id");
    inputDealers.setAttribute("value", dealer);

    // Set the button value based on the tip
    var button = document.createElement("button");
    button.setAttribute("class", "btn btn-primary");
    button.setAttribute("type", "submit");
    button.textContent = tip + " HP";

    // Clear the modal content and add the new elements
    content.innerHTML = "";
    var form = document.createElement("form");
    form.setAttribute("action", "/dealers");
    form.setAttribute("method", "post");
    form.appendChild(inputTip);
    form.appendChild(inputDealers);
    form.appendChild(button);
    content.appendChild(form);

    // Display the modal
    modal.style.display = "block";

    // Set the click event for the close button
    span.onclick = function() {
        modal.style.display = "none";
    }

    // Set the click event for the modal background
    window.onclick = function(event) {
        if (event.target == modal) {
        modal.style.display = "none";
        }
    }
}