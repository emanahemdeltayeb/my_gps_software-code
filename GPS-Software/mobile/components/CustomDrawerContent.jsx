import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Image } from 'react-native';
import { DrawerContentScrollView } from '@react-navigation/drawer';
import Collapsible from 'react-native-collapsible';
import { ChevronDown, ChevronUp } from 'lucide-react-native';

const navigationItems = [
  {
    name: 'Home',
    screen: 'Home',
    subItems: [],
  },
  {
    name: 'Devices',
    screen: 'Devices',
    subItems: [
      { name: 'All Devices', screen: 'All Devices' },
      { name: 'Add Device', screen: 'Add Device' },
    ],
  },
  {
    name: 'Alerts',
    screen: 'Alerts',
    subItems: [],
  },
  {
    name: 'Reports',
    screen: 'Reports',
    subItems: [],
  },
  {
    name: 'Geofence',
    screen: 'Geofence',
    subItems: [],
  },
  {
    name: 'Settings',
    screen: 'Settings',
    subItems: [
      { name: 'Profile', screen: 'Profile' },
      { name: 'Preferences', screen: 'Preferences' },
      { name: 'Credits', screen: 'Credits' },
      { name: 'Users', screen: 'Users' },
    ],
  },
];

const CustomDrawerContent = (props) => {
  const [expandedItems, setExpandedItems] = useState({});
  const [hoveredItem, setHoveredItem] = useState(null);

  const toggleExpand = (itemName) => {
    setExpandedItems((prev) => ({ ...prev, [itemName]: !prev[itemName] }));
  };

  const navigateToScreen = (screenName) => {
    props.navigation.navigate(screenName);
  };

  return (
    <DrawerContentScrollView {...props}>
      {/* Add a logo at the top */}
        <Image
          source={require('../assets/logo.png')} // Replace with your logo file path
          style={styles.logo}
        />
      {navigationItems.map((item) => (
        <View key={item.name} style={styles.itemContainer}>
          <TouchableOpacity
            style={[
              styles.itemButton,
              hoveredItem === item.name && styles.hoveredItemButton, // Apply hover style
            ]}
            onPress={() =>
              item.subItems.length > 0 ? toggleExpand(item.name) : navigateToScreen(item.screen)
            }
            onMouseEnter={() => setHoveredItem(item.name)} // Set hover state
            onMouseLeave={() => setHoveredItem(null)} // Clear hover state
          >
            <Text style={styles.itemText}>{item.name}</Text>
            {item.subItems.length > 0 &&
              (expandedItems[item.name] ? <ChevronUp size={20} /> : <ChevronDown size={20} />)}
          </TouchableOpacity>
          {item.subItems.length > 0 && (
            <Collapsible collapsed={!expandedItems[item.name]}>
              {item.subItems.map((subItem) => (
                <TouchableOpacity
                  key={subItem.name}
                  style={styles.subItemButton}
                  onPress={() => navigateToScreen(subItem.screen)}
                >
                  <Text style={styles.subItemText}>{subItem.name}</Text>
                </TouchableOpacity>
              ))}
            </Collapsible>
          )}
        </View>
      ))}
    </DrawerContentScrollView>
  );
};

const styles = StyleSheet.create({
  logo: {
    width: '100%', // Adjust to fit your design
    height: 150, // Adjust to fit your design
    resizeMode: 'contain',
  },
  itemContainer: {
    marginBottom: 5,
  },
  itemButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
    backgroundColor: 'white', // Default background color
    borderRadius: 8, // Slightly rounded corners
  },
  hoveredItemButton: {
    backgroundColor: '#f0f0f0', // Background color on hover
  },
  itemText: {
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1,
  },
  subItemButton: {
    padding: 10,
    paddingLeft: 30,
  },
  subItemText: {
    fontSize: 14,
  },
});

export default CustomDrawerContent;
