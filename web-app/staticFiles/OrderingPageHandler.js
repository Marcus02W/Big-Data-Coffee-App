
window.onload = () => {
    const formData = new FormData();
    var username = document.cookie
                    .split("; ")
                    .find((row) => row.startsWith("username="))
                    ?.split("=")[1];
    var password = document.cookie
                    .split("; ")
                    .find((row) => row.startsWith("password"))
                    ?.split("=")[1];

    var url = new URL(window.location.href);
    var searchParams = new URLSearchParams(url.search);
    var parameterValue = searchParams.get('parameter');

    formData.append("shop_id", parameterValue);
    formData.append("username", username);
    formData.append("password", password);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/ordering_page_api");
    xhr.send(formData);
    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4){
            response = xhr.responseText;
            response = JSON.parse(response);
            console.log(response);
  
            // Get the table container element
            var tableContainer = document.getElementById("tableContainer");
  
            // backend response is parsed into a HTML table format
            response.forEach(function(rowData) {

                // Creating row element
                var row = document.createElement("div");
                row.classList.add("row");
            
                // Creating cell elements for rows
                rowData.forEach(function(cellData) {
                var cell = document.createElement("div");
                cell.textContent = cellData;
                row.appendChild(cell);
                });
            
                // Creating the quantity control element
                var quantityControl = document.createElement("div");
                quantityControl.classList.add("quantity-control");
            
                var minusButton = document.createElement("button");
                minusButton.textContent = "-";
                quantityControl.appendChild(minusButton);
            
                var quantityInput = document.createElement("input");
                quantityInput.type = "number";
                quantityInput.value = "0";
                quantityControl.appendChild(quantityInput);
            
                var plusButton = document.createElement("button");
                plusButton.textContent = "+";
                quantityControl.appendChild(plusButton);
            
                row.appendChild(quantityControl);
            

                // Appending row to the table
                tableContainer.appendChild(row);


                // Event listener for minus button
                minusButton.addEventListener("click", function() {
                    var currentQuantity = parseInt(quantityInput.value);
                    if (currentQuantity > 0) {
                    quantityInput.value = currentQuantity - 1;
                    }
                });


                // Event listener for plus button
                plusButton.addEventListener("click", function() {
                    var currentQuantity = parseInt(quantityInput.value);
                    quantityInput.value = currentQuantity + 1;
                });
            });
        }
            

            
        
    }
}

// Function to process the user inputs (this function executes the order and sends all the required details to the backend)
function processInputs() {
    var rows = document.getElementsByClassName("row");
    const orderItemsData = new FormData();

    order_items_list = [];

    for (var i = 0; i < rows.length; i++) {
        var cells = rows[i].querySelectorAll("div:not(.quantity-control)");
        var quantityInput = rows[i].querySelector("input");
        var quantity = parseInt(quantityInput.value);
    
        var rowData = Array.from(cells).map(function(cell) {
        return cell.textContent.trim();
        });
    
        rowData.push(quantity);
    
        //console.log("Row " + (i + 1) + " data:", rowData);

        order_items_list.push(rowData);

        


    }
    var username = document.cookie
    .split("; ")
    .find((row) => row.startsWith("username="))
    ?.split("=")[1];
    var url = new URL(window.location.href);
    var searchParams = new URLSearchParams(url.search);
    var parameterValue = searchParams.get('parameter');
    console.log(order_items_list);

    var jsonOrderItems = JSON.stringify(order_items_list);
    console.log(jsonOrderItems);

    orderItemsData.append("order_items", jsonOrderItems);
    orderItemsData.append("customer_id", username);
    orderItemsData.append("shop_id", parameterValue);

    console.log(orderItemsData['order_items'])

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/order_processing_api");
    xhr.send(orderItemsData);
    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4){
            response = xhr.responseText;
            console.log(response)
            document.getElementById("response").innerHTML="Your order has been sent and will be processed soon. You will get routed back to the overview page now."
            setTimeout(() => {
                window.location.href = '/customer_landing';
              }, 3000);
        }
    }


    }