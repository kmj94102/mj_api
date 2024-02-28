var input = document.getElementById("imageInput");
var initLabel = document.getElementById("initLabel");

document.addEventListener("DOMContentLoaded", async function() {
    const column = document.getElementById("preview");
    new Sortable(column, {
        group: "shared",
        animation: 150,
        ghostClass: "blue-background-class"
      });
});

function addImage() {
    const preview = document.getElementById("preview");
    const input = document.getElementById("image");
  
    const img = el("img", {
        className: "embed-img",
        src: input.value,
        'data-url': input.value
    });
    const remove = el("img", {
        class: "remove",
        src: './img_close.png',
    })
    const imgContainer = el("div", { className: "container-img" }, img, remove);
    preview.append(imgContainer);

    remove.addEventListener('click', async () => {
        imgContainer.remove();
    });

    input.value = '';
}

document.getElementById("register").addEventListener('click', async function() {
    const images = document.querySelectorAll('.embed-img');
    const array = Array.from(images).map((item, _) => { return item.dataset.url });
    const category = document.getElementById('category');
    const productName = document.getElementById('productName');
    const price = document.getElementById('price');

    const data = {
        category: category.value,
        name:productName.value,
        price:price.value,
        urlList:array
    }

    fetch('https://port-0-mj-api-e9btb72blgnd5rgr.sel3.cloudtype.app/purchase/insert/goods', {
         method: 'POST',
         headers: {
             'Content-Type': 'application/json'
         },
         body: JSON.stringify(data)
     })
     .then(response => response.json())
     .then(_ => {
        alert(data.name + ' 등록 성공');
     })
     .catch(error => {
        alert('등록 실패');
        console.error('Error:', error);
     });
});

function el(nodeName, attributes, ...children) {
    const node =
      nodeName === "fragment"
        ? document.createDocumentFragment()
        : document.createElement(nodeName);
  
    Object.entries(attributes).forEach(([key, value]) => {
      if (key === "events") {
        Object.entries(value).forEach(([type, listener]) => {
          node.addEventListener(type, listener);
        });
      } else if (key in node) {
        try {
          node[key] = value;
        } catch (err) {
          node.setAttribute(key, value);
        }
      } else {
        node.setAttribute(key, value);
      }
    });
  
    children.forEach((childNode) => {
      if (typeof childNode === "string") {
        node.appendChild(document.createTextNode(childNode));
      } else {
        node.appendChild(childNode);
      }
    });
  
    return node;
}