import axios from "axios";

const handleSearch = async () => {
  try {
    const response = await axios.get("http://localhost:5000/api/search", {
      params: {
        activity,
        location,
        date: selectedDate?.toISOString(), // Format date properly
      },
    });

    // Store results in state or navigate with results
    console.log(response.data);
  } catch (error) {
    console.error("Search failed:", error);
  }
};
