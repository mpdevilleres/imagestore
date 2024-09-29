db = db.getSiblingDB("image_db");
db.createCollection("frames");

// since we want to to search by depth,
// it would be nice to have an index to improve its performance
db.image_db.createIndex({ "filename": 1, "depth": 1 });
