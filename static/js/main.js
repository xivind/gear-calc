// static/js/main.js
document.addEventListener('DOMContentLoaded', function () {
    // Initialize TomSelect for all select elements with class 'tom-select'
    document.querySelectorAll('.tom-select').forEach((el) => {
        new TomSelect(el, {
            create: false,
            sortField: {
                field: "text",
                direction: "asc"
            }
        });
    });
});

async function deleteItem(url) {
    if (!confirm('Are you sure you want to delete this item?')) return;

    try {
        const response = await fetch(url, {
            method: 'DELETE'
        });

        if (response.ok) {
            window.location.reload();
        } else {
            alert('Failed to delete item');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred');
    }
}
