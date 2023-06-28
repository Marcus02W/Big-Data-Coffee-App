window.onload = () => {
    const formData = new FormData();

    // accessing the login credentials from the cookie
    var username = document.cookie
                    .split("; ")
                    .find((row) => row.startsWith("username="))
                    ?.split("=")[1];
    var password = document.cookie
                    .split("; ")
                    .find((row) => row.startsWith("password"))
                    ?.split("=")[1];
    console.log(username);
    console.log(document.cookie);
    formData.append("username", username);
    formData.append("password", password);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/customer_page_api");
    xhr.send(formData);

    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4){
            response = xhr.responseText;
            response = JSON.parse(response);
            console.log(response);


            // === part for building the logic behind the left section (coffee shops overview with rating functionality and ordering link) ===
            const tableBody = document.getElementById('table-coffee-shops');

            // function to create a star element
            function createStar(index, shop_id) {
              const star = document.createElement('span');
              star.classList.add('star');
              star.classList.add('gray');
              star.addEventListener('click', function() {
                const rating = index + 1;
                //console.log(rating, shop_id);

                const formDataRating = new FormData();
                formDataRating.append("customer_id", username);
                formDataRating.append("shop_id", shop_id);
                formDataRating.append("score", rating);
                var xhr = new XMLHttpRequest();
                xhr.open("POST", "/rating_update_api");
                xhr.send(formDataRating);
                xhr.onreadystatechange = () => {
                  if (xhr.readyState === 4){
                    location.reload();
                  }
                }
              });
              return star;
            }


            // backend response is parsed into a HTML table format
            response['coffee_shops_overview'].forEach((row) => {
              const tableRow = document.createElement('tr');

              row.forEach((cell, index) => {
                const tableCell = document.createElement('td');

                if (index===0){
                  return;
                }
                  
                else if (index === 3) { // Identifying the score cell
                  const starsContainer = document.createElement('div');
                  starsContainer.classList.add('stars-container');

                  // Determine the rating value (number of golden stars)
                  const rating = cell ? parseInt(cell) : 0;

                  // Creating 5 stars, coloring the golden ones based on the rating
                  for (let i = 0; i < 5; i++) {
                    const star = createStar(i, row[0]);
                    if (i < rating) {
                      star.classList.remove('gray');
                      star.classList.add('golden');
                    }
                    starsContainer.appendChild(star);
                  }

                  tableCell.appendChild(starsContainer);
                } else {
                  tableCell.textContent = cell;
                }

                tableRow.appendChild(tableCell);
              });

              // link for ordering is created in this part
              tableCell = document.createElement('td');
              var link = document.createElement('a');

              // creating dynamic link for ordering at a specific coffee shop
              link.href = 'ordering_page?parameter=' + row[0]; // with row[0] the shop_id is appended to the url

              var linkText = document.createTextNode('Order now');
              link.appendChild(linkText);

              tableCell.appendChild(link);

              tableRow.appendChild(tableCell);

              tableBody.appendChild(tableRow);
            });



            // === part for building the logic behind the top right section (recent orders) ===
            const tableBodyOrders = document.getElementById('table-recent-orders');

            // backend response is parsed into a HTML table format
            response['recent_orders_overview'].forEach((row) => {
              const tableRow = document.createElement('tr');
            
              row.forEach((cell) => {
                const tableCell = document.createElement('td');
                tableCell.textContent = cell;
                tableRow.appendChild(tableCell);
              });
            
              tableBodyOrders.appendChild(tableRow);
            });



            // === part for building the logic behind the bottom right section (most critical ratings) ===
            const tableBodyRatings = document.getElementById('table-ratings');

            // backend response is parsed into a HTML table format
            response['ratings_overview'].forEach((row) => {
              const tableRow = document.createElement('tr'); 
            
              row.forEach((cell) => {
                const tableCell = document.createElement('td');
                tableCell.textContent = cell;
                tableRow.appendChild(tableCell);
              });
            
              tableBodyRatings.appendChild(tableRow);
            });
            

        }
    }
}