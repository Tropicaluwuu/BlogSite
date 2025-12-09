function likePost(postId) {
  const select = document.getElementById("likeUserSelect");
  if (!select || !select.value) {
    alert("Please select a user to like as.");
    return;
  }
  const userId = select.value;
  // Redirect to the like route
  window.location.href = `/posts/${postId}/like/${userId}`;
}
