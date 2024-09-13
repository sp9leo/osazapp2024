// Copyright (c) 2024,   and contributors
// For license information, please see license.txt


// frappe.ui.form.on("RFID", {
//         validate(frm) {
//         status_change = doc.has_value_changed("status");
//         if status_change:
//         console.log("status"+status_change);
//             // pass
//                 }
//     });


// frappe.ui.form.on("RFID", {
//   ucenec(frm) {
//     if (!frm.doc.ucenec) {
//       frappe.db.get_doc("Ucenec", null, { rfid: frm.doc.name }).then(doc => {
//         console.log(doc);
//         frappe.db.set_value("Ucenec", doc.name, "rfid", "");
//       });
//     } else {
//       frappe.db.get_doc("Ucenec", frm.doc.ucenec, { rfid: frm.doc.name })
//         .then(doc => {
//           console.log(doc);
//           frappe.db.set_value("Ucenec", doc.name, "rfid", frm.doc.name);
//         });
//     }
//   }
// });

// frappe.ui.form.on("RFID", {
//   validate(frm) {

//     if (frm.doc.ucenec =""){
//         frappe.db.get_doc("Ucenec", null, {rfid:frm.doc.name});
//         console.log("this one gets deleted");

//     }

// else{
//              // Function to update the property status
// function updatePropertyStatus(propertyId) {
//     // Assume you have a way to fetch the property data based on its ID
//     // For example, using an API call or directly from the DOM

//     // Update the property status to "Rented"
//     propertyId.then((value) => {
//         console.log(value); // This is a fulfilled promise 👈
//         console.log()
//         console.log(value.rfid)
//         frappe.db.set_value("Ucenec", frm.doc.ucenec, "rfid", frm.doc.name)
//     }).catch((err) => {
//         console.error(err);

//     });

//     // property.rfid = frm.doc.name;

//     // Save the updated property data (e.g., via an API call)
//     // ...

//     // Optionally, notify the user that the property status has been updated
//     alert('Property status updated to "Rented"');

//     //   frappe.db.get_doc("Ucenec", frm.doc.ucenec, { rfid: frm.doc.rfid }).then(doc => {
//     //     console.log(doc);
//     //     frappe.db
//     //       .set_value("Ucenec", frm.doc.ucenec, "rfid", frm.doc.name)
//     //       .then(r => {
//     //         let doc = r.message;
//     //         console.log(doc);
//     //       });
//     //   });
//     //   console.log("triggered");
//     // } else {

//     //     frappe.db.get_doc("Ucenec", frm.doc.ucenec, { rfid: frm.doc.rfid }).then(doc => {
//     //         console.log(doc);
//     //         frappe.db
//     //           .set_value("Ucenec", frm.doc.ucenec, "rfid", frm.doc.name)
//     //           .then(r => {
//     //             let doc = r.message;
//     //             console.log(doc);
//     //           });
//     //       });
//     //   console.log("no student");
//     // }
// }
// const propertyId = frappe.db.get_doc("Ucenec", frm.doc.ucenec, { rfid: frm.doc.rfid }); // Replace with the actual property ID
// updatePropertyStatus(propertyId);

// }

// }
// });

// // Assuming you have a function to handle the creation of a new Payment record
// function createPayment(propertyId) {
//     // Your logic to create a new Payment record and link it to the property
//     // ...
//     console.log("new payment created")

//     // After successfully creating the Payment record:
//     updatePropertyStatus(propertyId);
// }

// // Function to update the property status
// function updatePropertyStatus(propertyId) {
//     // Assume you have a way to fetch the property data based on its ID
//     // For example, using an API call or directly from the DOM

//     // Update the property status to "Rented"
//     const property = getPropertyData(propertyId);
//     property.status = 'Rented';

//     // Save the updated property data (e.g., via an API call)
//     // ...

//     // Optionally, notify the user that the property status has been updated
//     alert('Property status updated to "Rented"');
// }

// // Example usage:
// const propertyId = 'your_property_id_here'; // Replace with the actual property ID
// createPayment(propertyId);
