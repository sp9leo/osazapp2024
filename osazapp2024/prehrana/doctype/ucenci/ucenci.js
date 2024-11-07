// Copyright (c) 2024,   and contributors
// For license information, please see license.txt

frappe.ui.form.on("Ucenci", {
  izberi_rfid(frm) {
    const ucenec = frm.doc.name;
    console.log(ucenec);

    frappe.prompt(
      {
        label: "Select RFID",
        fieldname: "rfid",
        fieldtype: "Link",
        options: "RFID", // Ensure this is the correct doctype name
        reqd: 1,
        primary_action_label: "Potrdi",
        get_query: function() {
          return {
            filters: {
              status: "Pripravljen",
              link_ucenec: ""
            }
          };
        }
      },
      values => {
        const selectedRfid = values.rfid;
        console.log(`Selected RFID: ${selectedRfid}`);

        frappe.db
          .get_doc("RFID", selectedRfid)
          .then(doc => {
            console.log(doc);
            console.log(ucenec);
            doc.status = "Aktiven";
            doc.link_ucenec = ucenec;

            // Use frappe.call to update the document
            frappe.call({
              method: "frappe.client.save",
              args: {
                doc: doc
              },
              callback: function(response) {
                if (!response.exc) {
                  frappe.show_alert(
                    `Učencu ${frm.doc.full_name} dodan RFID ${selectedRfid}`
                  );
                  frm.set_value("rfid", selectedRfid);                  
                  frm.save();
                } else {
                  frappe.warn(
                    "Prišlo je do napake pri posodabljanju dokumenta."
                  );
                }
              }
            });
          })
          .catch(error => {
            console.error("Error fetching RFID document:", error);
            frappe.warn("Prišlo je do napake pri pridobivanju dokumenta RFID.");
          });
      }
    );
  }
});

