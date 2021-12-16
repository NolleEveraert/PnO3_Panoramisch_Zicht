let viewer;
let panoramas = [];

function setup() {
  noCanvas();
  let foto = document.getElementById('foto');
  viewer = new PANOLENS.Viewer( { output: 'console' } );
  // const panorama = new PANOLENS.VideoPanorama( 'video.mp4', { autoplay: true } );
  let panorama = new PANOLENS.ImagePanorama( foto);
  viewer.add( panorama );
  }

  function draw() {
    let foto = document.getElementById('foto');
    let panorama = new PANOLENS.ImagePanorama(foto);
    viewer.add(panorama);
    viewer.setPanorama(panorama);
    //viewer.remove(oudePanorama);
    panoramas.push(panorama);
    if(frameCount % 500 == 0) {
    console.log(frameCount);
    }
    //frameRate(5);
    if(frameCount % 500 == 0) {
        for(let beeld of panoramas) {
            viewer.remove(beeld);
        }
        viewer.clearAllCache();
        panoramas = [];
    }
  }