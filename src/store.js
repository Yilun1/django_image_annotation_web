// store.js
import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex, axios)

export default new Vuex.Store ({
  state: {
    rowData: []
  },

  actions: {
    loadFiles ({ commit }) {
      axios
           .get('api/files/')
           .then(data => {
             let rowData = data.data
             commit('SET_FILES', rowData)
           })
           .catch(error => {
             console.log(error)
           })
    },

    postFile ({ dispatch, commit }, newFile) {
      const config = {
        onUploadProgress (e) {
          var percentCompleted = Math.round( (e.loaded * 5000) / e.total );
        }
      };
      try {
        axios.post('api/files/', newFile, config,
        { headers: {
          'Content-Type': 'multipart/form-data'
           }
        })
          .then(res => {
            commit('POST_FILE', newFile)
          })
          .then(res => {
            dispatch('loadFiles')
          })
      } catch (error) {
        console.log(error);
      }
    },

    deleteFile ({ dispatch }, result_id) {
      console.log("delete result id");
      console.log(result_id);
      axios.delete('api/files/' + result_id)
        .then(res => {
          dispatch('loadFiles')
          console.log(res)
        })
        .catch(error => {
          console.log(error)
      })
    },

    downloadFile ({ dispatch }, filename) {
      axios({
        url: `media/${filename}`,
        method: 'GET',
        responseType: 'blob',
      })
      .then ((res) => {
        const url = window.URL.createObjectURL(new Blob([res.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
      })
    }

/*    downloadFile ({ dispatch }, filename) {
      var index1=filename.lastIndexOf(".");
      var index2=filename.length;
      var suffix=filename.substring(index1+1,index2);
      console.log("suffix");
      console.log(suffix);
      if(suffix==="jpg"||suffix==="png"||suffix==="bmp"){
      window.location.href = "http://127.0.0.1:8000/canvas/"+filename;
      }else{alert("format: jpg png bmp");}

    }*/

  },

  mutations: {
    SET_FILES (state, files) {
      state.rowData = files
    },
    POST_FILE (state, newFile) {
      state.rowData.push(newFile)
    }
  }
})
