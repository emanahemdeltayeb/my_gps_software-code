import { useNavigation } from '@react-navigation/native';
import React, { useState } from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { List, Text, Button, Chip, Divider } from 'react-native-paper';
import { widthPercentageToDP as wp } from 'react-native-responsive-screen';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const AlertsScreen = () => {
  const navigator = useNavigation();

  const [alerts, setAlerts] = useState([
    { id: '1', title: 'New device connected', date: '2023-05-15', read: false },
    { id: '2', title: 'Battery low on Device XYZ', date: '2023-05-14', read: false },
    { id: '3', title: 'Firmware update available', date: '2023-05-13', read: true },
    { id: '4', title: 'Unusual activity detected', date: '2023-05-12', read: false },
    { id: '5', title: 'Monthly report ready', date: '2023-05-11', read: true, action: {"label": "Update", "screen": "Main"} },
  ]);

  const markAsRead = (id) => {
    setAlerts(alerts.map(alert => 
      alert.id === id ? { ...alert, read: true } : alert
    ));
  };

  const markAllAsRead = () => {
    setAlerts(alerts.map(alert => ({ ...alert, read: true })));
  };

  const renderItem = ({ item }) => (
    <List.Item
      title={item.title}
      description={item.date}
      left={() => (
        <View style={styles.iconContainer}>
          <Icon 
            name={item.read ? "bell-outline" : "bell-ring"}
            size={24} 
            color={item.read ? "#757575" : "#1976D2"}
          />
        </View>
      )}
      right={item.action ? () => (
        <View style={styles.rightContent}>
          <Chip mode="outlined" onPress={() => {navigator.navigate(item.action.screen)}} style={styles.categoryChip}>{item.action.label}</Chip>
        </View>
      ) : undefined}
      style={[
        styles.listItem,
        item.read ? styles.readItem : styles.unreadItem
      ]}
    />
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Alerts</Text>
        <Button mode="text" onPress={markAllAsRead}>
          Mark all as read
        </Button>
      </View>
      <FlatList
        data={alerts}
        renderItem={renderItem}
        keyExtractor={item => item.id}
        ItemSeparatorComponent={() => <Divider />}
        contentContainerStyle={styles.listContainer}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: wp('4%'),
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  listContainer: {
    paddingVertical: wp('2%'),
  },
  listItem: {
    paddingVertical: wp('2%'),
    paddingHorizontal: wp('4%'),
  },
  unreadItem: {
    backgroundColor: '#E3F2FD',
  },
  readItem: {
    backgroundColor: '#ffffff',
  },
  iconContainer: {
    justifyContent: 'center',
    marginRight: wp('2%'),
  },
  rightContent: {
    flexDirection: 'row',
    alignItems: 'center',
  }
});

export default AlertsScreen;

