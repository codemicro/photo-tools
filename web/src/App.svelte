<script>
import { each } from "svelte/internal";



	let inputClassifier = ""
	let inputFilmStock = ""
	let inputShots = 24
	let inputCamera = ""
	let inputLoadDate
	let inputLab = ""
	let inputDevDate
	let inputNotes = ""
	let selectCategory
	let inputCategoryDate
	let inputCategoryNote = ""
	let selectShot
	let inputShotNumber = 1
	let inputExposure = "+0"
	let inputShutterSpeed = ""
	let inputAperture = ""
	let inputShotNote = ""

	// category: {"date", "notes", "data"}
	// shot: {"shot_number", "exposure", "shutter_speed", "aperture", "notes"}
	let categories = []

	function formatDate(inputDate) {
		function format(m) {
			let f = new Intl.DateTimeFormat("en", m)
			return f.format(inputDate).toUpperCase()
		}
		return [{day: '2-digit'}, {month: 'short'}, {year: '2-digit'}].map(format).join("")
	}

	function generate() {
		const dataBlock = {
			"classifier": inputClassifier,
			"film_stock": inputFilmStock,
			"shots": inputShots.toString(),
			"camera": inputCamera,
			"load_date": formatDate(new Date(inputLoadDate)),
			"lab": inputLab,
			"dev_date": formatDate(new Date(inputLoadDate)),
			"notes": inputNotes,
			"data": categories,
		}

		const link = document.createElement("a")
		link.type = "application/json"
		link.download = "shots.json"
		link.href = URL.createObjectURL(new Blob([JSON.stringify(dataBlock)]))
		link.click()

		location.reload()
	}

	function addCategory() {
		if (inputCategoryDate === undefined) {
			return
		}

		categories = [...categories, {"date": formatDate(new Date(inputCategoryDate)), "notes": inputCategoryNote, "data": []}]
		inputCategoryDate = undefined
		inputCategoryNote = ""
	}

	function removeCategory() {
		if (selectCategory === undefined) {
			return
		}
		let x = categories.slice(0, selectCategory)
		let y = categories.slice(selectCategory + 1, categories.length)
		categories = x.concat(y)
		selectCategory = undefined
	}

	function addShot() {
		if (selectCategory === undefined) {
			return
		}

		let shot = {
			"shot_number": inputShotNumber.toString(),
			"exposure": inputExposure,
			"shutter_speed": inputShutterSpeed,
			"aperture": inputAperture.charAt(0).toLowerCase() !== "f" ? "f" + inputAperture : inputAperture,
			"notes": inputShotNote,
		}

		categories[selectCategory].data.push(shot)
		categories = categories

		inputShotNumber += 1
		inputExposure = "+0"
		inputShutterSpeed = ""
		inputAperture = ""
		inputShotNote = ""
	}

</script>

<main>
	<div class="mt-5 mb-5 container">
        
        <div class="row mb-2">
            <div class="col-2">
                <label for="inputClassifier" class="col-form-label">Classifier</label>
            </div>
            <div class="col">
                <input type="text" id="inputClassifier" class="form-control" bind:value={inputClassifier}>
            </div>
        </div>
        
        <div class="row mb-2">
            <div class="col-2">
                <label for="inputFilmStock" class="col-form-label">Film stock</label>
            </div>
            <div class="col">
                <input type="text" id="inputFilmStock" class="form-control" bind:value={inputFilmStock}>
            </div>
        </div>
        
        <div class="row mb-2">
            <div class="col-2">
                <label for="inputShots" class="col-form-label">Shots</label>
            </div>
            <div class="col">
                <input type="number" id="inputShots" class="form-control" bind:value={inputShots}>
            </div>
        </div>
        
        <div class="row mb-2">
            <div class="col-2">
                <label for="inputCamera" class="col-form-label">Camera</label>
            </div>
            <div class="col">
                <input type="text" id="inputCamera" class="form-control" bind:value={inputCamera}>
            </div>
        </div>
        
        <div class="row mb-2">
            <div class="col-2">
                <label for="inputLoadDate" class="col-form-label">Load date</label>
            </div>
            <div class="col">
                <input type="date" id="inputLoadDate" class="form-control" bind:value={inputLoadDate}>
            </div>
        </div>
        
        <div class="row mb-2">
            <div class="col-2">
                <label for="inputLab" class="col-form-label">Lab</label>
            </div>
            <div class="col">
                <input type="text" id="inputLab" class="form-control"  bind:value={inputLab}>
            </div>
        </div>
        
        <div class="row mb-2">
            <div class="col-2">
                <label for="inputDevDate" class="col-form-label">Dev date</label>
            </div>
            <div class="col">
                <input type="date" id="inputDevDate" class="form-control"  bind:value={inputDevDate}>
            </div>
        </div>
        
        <div class="row mb-2">
            <div class="col-2">
                <label for="inputLab" class="col-form-label">Notes</label>
            </div>
            <div class="col">
                <textarea id="inputNotes" rows="3"  bind:value={inputNotes}></textarea>
            </div>
        </div>
        
        <div class="container mt-5">
            <div class="row">
                <div class="col">
                    <select id="selectCategory" class="form-select mb-2" size="20" bind:value={selectCategory}>
						{#each categories as category, index}
							<option value={index}>{category.date} - {category.notes}</option>
						{/each}
                    </select>

                    <div class="mb-2">
                        <label for="inputCategoryDate" class="form-label">Date</label>
                        <input type="date" class="form-control" id="inputCategoryDate" bind:value={inputCategoryDate}>
                    </div>
                    <div class="mb-2">
                        <label for="inputCategoryNote" class="form-label">Note</label>
                        <input type="text" class="form-control" id="inputCategoryNote" bind:value={inputCategoryNote}>
                    </div>
                    <div class="mb-2">
                        <button type="button" class="btn btn-primary" id="buttonAddCategory" on:click={addCategory}>Add category</button>
                    </div>
                    <div class="mb-2">
                        <button type="button" class="btn btn-danger" id="buttonRemoveCategory" on:click={removeCategory}>Remove selected category</button>
                    </div>

                </div>
                <div class="col">
                    <select id="selectShot" class="form-select mb-2" size="20" bind:value={selectShot}>
						{#if selectCategory !== undefined}
							{#each categories[selectCategory].data as shot, index}
								<option value={index}>{shot["shot_number"]} - {shot.exposure}, {shot["shutter_speed"]}, {shot.aperture}, {shot.notes}</option>
							{/each}
						{/if}
					</select>
                </div>
                <div class="col">
                    
                    <div class="mb-2">
                        <label for="inputShotNumber" class="form-label">Shot number</label>
                        <input type="number" class="form-control" id="inputShotNumber" bind:value={inputShotNumber}>
                    </div>
                    <div class="mb-2">
                        <label for="inputExposure" class="form-label">Exposure</label>
                        <input type="text" class="form-control" id="inputExposure" bind:value={inputExposure}>
                    </div>
                    <div class="mb-2">
                        <label for="inputShutterSpeed" class="form-label">Shutter speed</label>
                        <input type="text" class="form-control" id="inputShutterSpeed" bind:value={inputShutterSpeed}>
                    </div>
                    <div class="mb-2">
                        <label for="inputAperture" class="form-label">Aperture</label>
                        <input type="text" class="form-control" id="inputAperture" bind:value={inputAperture}>
                    </div>
                    <div class="mb-3">
                        <label for="inputShotNote" class="form-label">Note</label>
                        <input type="text" class="form-control" id="inputShotNote" bind:value={inputShotNote}>
                    </div>
                    <div class="mb-2">
                        <button type="button" class="btn btn-primary" id="buttonAddShot" on:click={addShot}>Add shot</button>
                    </div>

                </div>
            </div>
        </div>
        
		<button type="button" class="btn btn-success" on:click={generate}>Download JSON</button>

    </div>
</main>