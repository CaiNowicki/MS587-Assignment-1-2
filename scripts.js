console.log("scripts.js file loaded");

function downloadStory(storyId) {
    console.log("downloadStory function called with ID: " + storyId);
    // Get story content via ID
    var storyContent = document.getElementById(storyId).innerText;
    console.log("Story content: " + storyContent);
    var blob = new Blob([storyContent], { type: "text/plain" });

    // Create URL to contain blob
    var link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = storyId + ".txt";
    link.click();
}
