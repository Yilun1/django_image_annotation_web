<template>
  <b-container>

    <br />

    <!-- PART-2: UPLOAD A FILE -->
    <b-card bg-variant="light">
      <b-form-file v-model="selFile"
                   ref="form"
                   placeholder="Drop a file here..."/>
      <b-button variant="primary" @click="submitFile()">
        Submit &nbsp; &nbsp;</b-button>
    </b-card>

    <br />

    <!-- PART-3: DELETE FILE(S) -->
    <b-card bg-variant="light">
      <b-row>
        <b-col col="4"><b-button variant="danger" @click="deleteFile()">
          Delete &nbsp;&nbsp;</b-button>
        </b-col>
        <b-col cols="4" md="auto">
          <b-card bg-variant="light" v-if="status">
            <b-card-text style="margin-right: 50px;">
              <strong>{{ selectedDataSizes.length }}</strong> File(s) selected</b-card-text>
            <b-card-text>Total size: <strong>{{ selectedDataTotal }}</strong></b-card-text>
          </b-card>
        </b-col>
      </b-row>

      <hr />

      <!-- PART-1: LIST FILES -->
      <ag-grid-vue style="width: 100%; height: 500px; border: 1px solid #e7e9ea; border-radius: 4px;"
                   class="ag-theme-material"
                   :row-height=60
                   :columnDefs="columnDefs"
                   :gridOptions="gridOptions"
                   :autoGroupColumnDef="autoGroupColumnDef"
                   :frameworkComponents="frameworkComponents"
                   :suppressRowClickSelection="true"
                   :groupSelectsChildren="true"
                   :debug="true"
                   :rowSelection="rowSelection"

                   :defaultColDef="{
                              enableValue: true,
                              sortable: true,
                              resizable: true,
                              filter: true
                              }"

                   :enableRangeSelection="true"
                   animateRows
                   @rowClicked = "onRowClicked"
                   @rowSelected = "onRowSelected"
                   :paginationAutoPageSize="true"
                   :pagination="true"
                   @gridReady="onGridReady"
                   :rowData="rowData">
      </ag-grid-vue>

  </b-card>

  <!-- PART-3: DELETE FILE(S) -->
  <!-- Modal Component -->
  <b-modal v-if="mShow" v-model="modal" @ok="handleOk" @cancel="$emit('close')">
      Selected file(s) will be deleted?
  </b-modal>
   <b-button variant="primary" @click="annotation">
        annotation &nbsp; &nbsp;</b-button>
  </b-container>
</template>

<script>
import {AgGridVue} from "ag-grid-vue"
import filetypeCellRenderer from "../filetypeCellRenderer" // uploaded file type validator

import { mapState } from 'vuex'
import { sizeFormatter, dateFormatter } from '../utils'
import axios from "axios"; // Ag-grid display format for file size and date
var selectedDataStringPresentation = "";
var set_rowdata;
export default {
  data () {
    return {
      selFile: null,
      columnDefs: null,
      autoGroupColumnDef: null,
      frameworkComponents: null,
      rowSelection: null,
      gridOptions: {},
      modal: false,
      mShow: false,
      result_id: null,
      status: false,
      selectedDataSizes: [],
      selectedDataTotal: 0
    }
  },
  components: {
      AgGridVue
  },

  beforeMount() {
    this.columnDefs = [
        {
          headerName: 'Name',
          field: 'name',
          width: 300,
          filterParams: { newRowsAction: "keep" },
          checkboxSelection: params => {
            return params.columnApi.getRowGroupColumns().length === 0;
          },
          headerCheckboxSelection: function(params) {
            return params.columnApi.getRowGroupColumns().length === 0;
          },
        },
        {
          headerName: 'Filetype',
          field: 'filetype',
          width: 55,
          cellRenderer: 'filetypeCellRenderer',
          filterParams: { newRowsAction: "keep" },
        },
        {
          headerName: 'Size',
          field: 'size',
          valueFormatter: sizeFormatter,
          width: 55,
          filterParams: { newRowsAction: "keep" }
        },
        {
          headerName: 'Added',
          field: 'since_added',
          width: 90,
          sort: 'desc',
          valueFormatter: dateFormatter
        }
    ]

    this.frameworkComponents = {
      filetypeCellRenderer: filetypeCellRenderer
    }

    this.autoGroupColumnDef = {
      headerName: "Group",
      width: 250,
      field: "name",
      valueGetter: params => {
        if (params.node.group) {
          return params.node.key;
        } else {
          return params.data[params.colDef.field];
        }
      },
      headerCheckboxSelection: true,
      cellRenderer: "agGroupCellRenderer",
      cellRendererParams: { checkbox: true }
    };

    this.rowSelection = "multiple";

  },
  mounted () {
    this.$store.dispatch('loadFiles')
    this.gridOApi = this.gridOptions.api;
    console.log("mounted called")
  },

  computed: {
    ...mapState([
      'rowData'
    ])

  },
  methods: {

    onGridReady(params) {
      this.gridApi = params.api;
      this.columnApi = params.columnApi;
      params.api.sizeColumnsToFit();
      params.api.setRowData();
      console.log("onGirdReady called");
    },

    onRowSelected (event) {
      const selectedNodes = this.gridApi.getSelectedNodes();
      const selectedData = selectedNodes.map( node => node.data );
      selectedDataStringPresentation = selectedData.map( node => node.name ).join(', ');    //删除这个空格和file_id
      console.log("selected_filename: ", selectedDataStringPresentation);
      this.selectedDataSizes = selectedData.map(node => node.size)

      // get the total size
      const add = (a, b) => a + b
      if (this.selectedDataSizes.length > 0) {
        this.status = true
        const totalSize = {value: this.selectedDataSizes.reduce(add)}
        this.selectedDataTotal = sizeFormatter(totalSize)
      } else { this.status = false }
    },

    submitFile () {
      if (this.selFile.size < 5 * 1024 * 1024) {
        var vm = this
        const fd = new FormData()
        fd.append('file', vm.selFile)    //上面v-model = selfile 详解
        this.$store.dispatch('postFile', fd)
      } else {
        alert("File size must be smaller than 5MB")
      }
    },

    deleteFile () {
      const selectedNodes = this.gridApi.getSelectedNodes()
      if (selectedNodes.length > 0) {
        const selectedData = selectedNodes.map( node => node.data );
        const result_id = selectedData.map( node => node.file_id)
        console.log("selected_file_id: ", result_id)
        this.result_id = result_id
        this.mShow = true
        this.modal = true
      }
    },

    handleOk () {
      this.$store.dispatch('deleteFile', this.result_id)
      this.mShow = false
      this.status = false
      console.log("handleOk called")
    },

    onRowClicked(event) {
      let file_id = event.node.data.file_id
      let filename = event.node.data.name
      this.$store.dispatch('downloadFile', filename)

    },
    annotation(){
      if(selectedDataStringPresentation!=="")
      {
        var current_file_id;
        var file_id_max = 0;
        this.gridApi.forEachNode((rowNode, index) => {

          current_file_id = rowNode.data.file_id
          if(current_file_id>file_id_max){file_id_max = current_file_id}
        });

        var filenames_selected =selectedDataStringPresentation.split(",");
        var filetype_selected_index;
        var filetype_suffix;
        var filetype_image_flag = true;
        for(var i=0;i<filenames_selected.length;i++)
        {
            filetype_selected_index = filenames_selected[i].lastIndexOf(".");
            filetype_suffix = filenames_selected[i].substring(filetype_selected_index+1,filetype_selected_index+4);
            if((filetype_suffix!=="jpg")&&(filetype_suffix!=="png")&&(filetype_suffix!=="bmp")&&(filetype_suffix!=="jpeg")
            &&(filetype_suffix!=="JPG")&&(filetype_suffix!=="PNG")&&(filetype_suffix!=="BMP")&&(filetype_suffix!=="JPEG"))
            {filetype_image_flag = false;}
        }
        if(filetype_image_flag === true)
        {window.location.href = "multifiles/"+selectedDataStringPresentation;}else{
          alert("please only select images of jpg or png or bmp format")
        }
      }else{
        alert("please select one or multiple files")
      }
    },

  }
}

</script>

<style lang="scss">

// $primary-color: #2196F3; // blue-500
// $accent-color: green; // amber-A200

@import "~ag-grid-community/dist/styles/ag-grid.css";
@import "~ag-grid-community/dist/styles/ag-theme-balham.css";
@import "~ag-grid-community/dist/styles/ag-theme-bootstrap.css";
@import "~ag-grid-community/dist/styles/ag-theme-material.css";

.ag-theme-material {
  font-size: 16px;
  font-family: Questrial, Roboto;
}

.ag-theme-material .ag-row, .ag-theme-material .ag-row:not(.ag-row-first) {
  padding-top: 7px;
}

.ag-theme-material .ag-icon-checkbox-checked:empty {
  background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAC2ElEQVR42tWaPWhTURTHgzZ+QkWk0KWLZKiERPJNaCtBqYODQyRFbP3oaEdxfGPH0klwEXGwg+AQ3Sy4iC5VwclJBzEFKa04tKSV1vj/Q+t9fb70vCZe33mBQ5J3zr33/7s59917c1+s1Wr9ZZlMppzL5ZxsNvsM74uwVki2uK3BoSY/rbu+IPBEPp9/yMIajdqo0RcAziE4GwxUbg1q3QVAqjbiNxD8Fu/1MIxtU4MfBDX/AfBJm1XYVCKROEx/mEYN1EJN3nSif2fAesUP0qnJqMkLQe10OB6AKRbQaNTm0erEeJty57yQNgrSyYwJao+57/McNCH2bhztX4Vl9oqjRvc8EfP8JPUwxFcqlSNo+51Lx1wqlTrZBrTu1qwBgGk86zcLwy5qB6D4EbS71WbSasIG1QKk0+njaPOzsHy4ohWAbd8Xlg0rxWLxlEoA9OyoIJ52Td8YMGuvr3uJx9h4ylitAI+Enl/CMqFPIwBT57Ignr1fZaw6AA5ItPFNAHjMWI0AbOuJtIXkDKwSAGkxFmDLeImx6gAKhUI/6l4WAB4wViUAeva5IP5LqVTqtQpQLpePIg0mYdVarXZwH3l/UxD/C7fMC4y1BsCBBd9790YimUweCpA6A4j/IeT9PcZaA+Cs6dlEyBCm7LzQ+59gx6wCQOgb4w8OAf9tQfwWbJix1gCQm+eMLzAEU+c0fKtC2RnG2gbow7X1/UDgdQDXXgllPnIbaRfApNA4rm8GhcDnO0LsZgEv1m0fwEBM7Gz7BHsJawqg06zTKoAE0YV9gMWtAggz6vUuIH5iTJ1lPdYBBIgbHUI4LB8SgAwh5P0C7jo9SgDMGicgRBMAZ1hGD4AZ2LcCQNxlrC6A4BCvObHpBTAQkz4Qa7ieoN8mwD/7e51retTxYruu7xB/vnvB8t/rnR1wyHuA+P864Ij8EVPkD/mifcwa/YPu6D9qEP2HPSL/uM1vzeJjU/DsstoAAAAASUVORK5CYII=');
}

.ag-cell-focus,.ag-cell-no-focus{
  border:none !important;
}

.ag-root-wrapper-body.ag-layout-normal {
  border-radius: 4px;
}

/* Style buttons */
.btn {
  margin-top: 20px;
  border: none; /* Remove borders */
  color: white; /* White text */
  padding: 12px 16px; /* Some padding */
  font-size: 16px; /* Set a font size */
  cursor: pointer; /* Mouse pointer on hover */
}
/* Darker background on mouse-over */
.btn:hover {
  background-color: Gray;
}


</style>
