document.addEventListener("DOMContentLoaded", () => {
    const noteForm = document.getElementById("note-form");
    const noteInput = document.getElementById("note-input");
    const notesContainer = document.getElementById("notes-container");
  
    // Load notes from localStorage
    let notes = JSON.parse(localStorage.getItem("notes")) || [];
  
    // Save notes to localStorage
    const saveNotes = () => {
      localStorage.setItem("notes", JSON.stringify(notes));
    };
  
    // Render notes
    const renderNotes = () => {
      notesContainer.innerHTML = ""; // Clear existing notes
      notes.forEach((note, index) => {
        const noteDiv = document.createElement("div");
        noteDiv.className = "note";
  
        const input = document.createElement("input");
        input.type = "text";
        input.value = note;
        input.addEventListener("input", (e) => {
          notes[index] = e.target.value; // Update note on edit
          saveNotes(); // Save updated notes
        });
  
        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Delete";
        deleteButton.addEventListener("click", () => {
          notes.splice(index, 1); // Remove note
          saveNotes(); // Save updated notes
          renderNotes(); // Re-render notes
        });
  
        noteDiv.appendChild(input);
        noteDiv.appendChild(deleteButton);
        notesContainer.appendChild(noteDiv);
      });
    };
  
    // Add a new note
    noteForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const noteText = noteInput.value.trim();
      if (noteText) {
        notes.push(noteText);
        saveNotes(); // Save updated notes
        noteInput.value = "";
        renderNotes(); // Re-render notes
      }
    });
  
    renderNotes(); // Initial render
  });
  