let menuicn = document.querySelector(".menuicn");
let nav = document.querySelector(".navcontainer");

menuicn.addEventListener("click",()=>
{
	nav.classList.toggle("navclose");
})

// assume dashboardData is an array of objects with properties like 'title' and 'summary'
const dashboardData = [
	{ title: 'Revenue', summary: 'Total revenue: $10,000' },
	{ title: 'Expenses', summary: 'Total expenses: $5,000' },
	{ title: 'Profit', summary: 'Total profit: $5,000' },
	{ title: 'Sales by Products', summary: 'Top selling product: Product A' },
	{ title: 'Expense by category', summary: 'Top expense category: Category A' }
  ];
  
  // add an event listener to the search button
  searchButton.addEventListener("click", function() {
	// get the search query from the input field
	const searchQuery = searchInput.value.toLowerCase();
	
	// filter the dashboard data based on the search query
	const filteredData = dashboardData.filter(function(item) {
	  // convert item title and summary to lowercase and check if they contain the search query
	  return item.title.toLowerCase().includes(searchQuery) ||
			 item.summary.toLowerCase().includes(searchQuery);
	});
	
	// do something with the filtered data, such as update the dashboard display
	console.log(filteredData);
  });